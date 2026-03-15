# Released under the MIT license see LICENSE

import binascii
import machine
import network
import rp2
import utime as time
import urequests as requests
from lib.umqtt.simple import MQTTClient         # https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py

rp2.country('DE')


class WlanMqtt():
    """class for connecting to a WLAN MQTT Broker.

    Status led is switched on during connection setup, when connection is established it goes out.
    Collects all messages in self.mqtt_result.
    The messages themselves are subscribed to by a json file
    Example in the __main__ area
    Format of the json file:
      {"sma": {
            "P_AC": ["sma_solar", "5.1f"],
            "STIME": ["sma_time", ""]
            },
        "Smartmeter": {
              "1-0:16.7.0": ["current_power", [:-2]]
              },
              
    --> subscribed for:
        "sma/P_AC" and assigns the received messages to the variable self.mqtt_result["sma_solar"]
        "sma/STIME" and assigns the received messages to the variable self.mqtt_result["sma_time"]
        "Smartmeter/1-0:16.7.0" and assigns the received messages to the variable self.mqtt_result["current_power"]       
    """

    def __init__(self, server, wlSsid, wlPw, led, clientid=None):
        """
        Initialisation for the WLAN MQTT client.

        server : str
            ip Adresse from the broker, e.q = "192.178.158.22"
        wlPw : str
            password for your wlan Server
        wlSsid: str
            name from the Server
        """
        self.led = led    # Status LED
        self.mqtt_result = {}
        self.msg = ""
        while True:
            status = self._wlanConnect(wlSsid, wlPw)
            if status >= 3:
                break
            print('Restart Wlan connection')
        print('Start Mqtt connection')
        clientid = binascii.hexlify(machine.unique_id()) if clientid is None else clientid
        self.mqtt = MQTTClient(clientid, server)
        print(f"Client {clientid} connected to {server}")

    def init(self, topics, lastwill=None):
        """
        Set the callback.

        Subscribed messages will be delivered to this callback.
        Results are stored to mqtt_result.

        topics: dict
            e.q. {"sma": {"P_AC": ["sma_solar", int]}    topic = sma.P_AC,
                                                         value is an integer, saved to mqtt_result[sma_solar]
        """
        def topicstr(subtopic, mqttstr=None):
            for ssubtopic in subtopic.keys():
                if type(subtopic[ssubtopic]) is list:
                    print(f" subscribe to {mqttstr}/{ssubtopic}, set mqtt_result['{subtopic[ssubtopic][0]}]")
                    self.mqtt_result[subtopic[ssubtopic][0]] = 0
                    self.mqtt.subscribe(f"{mqttstr}/{ssubtopic}")
                else:
                    mqttstr = topicstr(subtopic[ssubtopic], f'{mqttstr}/{ssubtopic}' if mqttstr is not None else ssubtopic)
            return mqttstr[:mqttstr.find('/')] if mqttstr is not None and mqttstr.find('/') > 0 else None

        self.topics = topics
        self.mqtt.set_callback(self._sub_callback)
        if lastwill is not None:
            lastwill = lastwill.split(',')
            self.mqtt.set_last_will(lastwill[0], lastwill[1], retain=False, qos=0)
        self.mqtt.connect()        
        topicstr(topics)
        
    def reconnect(self):
        print('Failed to connect to MQTT broker, Reconnecting...' % (server))
        time.sleep(5)
        mqtt.reconnect()    
        
    def disconnect(self):
        self.mqtt.disconnect()
        self.wlan.disconnect()
        self.wlan.deinit()

    @property
    def status(self):
        if self.wlan.isconnected():
            return self.wlan.status()
        else:
            return -1

    def _sub_callback(self, topic, msg):
        topic = topic.decode('utf-8').split('/')
        msg = msg.decode('utf-8')
        searchtopic = self.topics
        index = 0
        while index < len(topic):        # search for the corresponding variable name
            if topic[index] in searchtopic.keys():
                searchtopic = searchtopic[topic[index]]
                index += 1
            else:
                print('Error: topic {topic} not found in topics')
                return
        msg = f"{float(msg):{searchtopic[1]}}" if len(searchtopic)>1 else msg       # format
        msg = f"{msg}{searchtopic[2]}" if len(searchtopic)>2 else msg               # add post message
        self.mqtt_result[searchtopic[0]] = msg

    def _wlanConnect(self, wlSsid, wlPw):
        """ Create the WLAN-Connection."""
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            print('WLAN setup connection')
            wlan.deinit()            
            wlan.active(True)
            print('WLAN enabled')
            time.sleep(2)
            wlan.connect(wlSsid, wlPw)
            for i in range(10):
                status = wlan.status()
                if status < 0 or status >= 3:
                    break
                self.led.toggle()
                print('->', status)
                time.sleep(0.5)
        if wlan.isconnected():
            print('WLAN connection ok')
            self.led.on()
            status = wlan.status()
            print('WLAN state:', status)
            netConfig = wlan.ifconfig()
            print('IPv4-Adresse:', netConfig[0], '/', netConfig[1])
            print('Standard-Gateway:', netConfig[2])
            print('DNS-Server:', netConfig[3])
            time.sleep(3)
            self.led.off()
            self.wlan = wlan
        else:
            print('No WLAN connection')
            self.led.off()
            status = wlan.status()
            print('WLAN state:', status)
        return status


if __name__ == "__main__":
    from config import SERVER, WlSsid, WlPw
    from config import TOPICS

    led = machine.Pin('LED', machine.Pin.OUT, value=0)
    client = WlanMqtt(SERVER, wlSsid=WlSsid, wlPw=WlPw, led=led)
    topics = {"sma": {"P_AC": ["solar", int]}}           # get Topic "sma\P_AC" This should be change to your Topic
    topics = TOPICS
    client.init(topics)
    try:
        lasttime = time.time() - 9
        while 1:
            # micropython.mem_info()
            client.mqtt.wait_msg()
            if (time.time() - lasttime) > 10:
                print(client.mqtt_result)                  # all received topics are in mqtt_result
                lasttime = time.time()                      
    finally:
        client.mqtt.disconnect()
