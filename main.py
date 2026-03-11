# Released under the MIT license see LICENSE

# without deepsleep ~57-65mA

import os
import gc
import time
import framebuf
import machine
from color_setup import ssd
from color_setup import ssdred
from update import Update
import config
import re
import gc

from gui.widgets.dial import Dial

from wlanmqtt import WlanMqtt
from tiles import Tiles

ssdred.fill(0)
ssd.fill(0)          # auf White setzen
led = machine.Pin('LED', machine.Pin.OUT, value=0)

tiles = Tiles(config.CONTENT)
updates = Update(led, state_topic=config.Topic)
# ssdred = None
rtc =machine.RTC()
gc.collect()

startuploop = True

while True:
    mqttclient = WlanMqtt(config.SERVER, wlSsid=config.WlSsid, wlPw=config.WlPw, led=led)
    mqttclient.init(config.TOPICS, f"{config.Topic},disconnect")
    # mqttclient.init(config.TOPICS,)    
    
    starttime = time.time()
    print(f"collect messages for {config.mqtt_waittime}s")    
    while time.time()-starttime < config.mqtt_waittime:           # collect mqtt messages
        time.sleep(1)
        mqttclient.mqtt.publish(config.Topic, b'collect')        
        while mqttclient.mqtt.check_msg():
            mqttclient.mqtt.wait_msg()
    print("   -> collecting done")

    while startuploop:                                            # set time at startup
        while mqttclient.mqtt.check_msg():
            mqttclient.mqtt.wait_msg()
        if mqttclient.mqtt_result['sma_time'] != 0:
            startuploop = False
        if not startuploop:
            regex = re.compile('[- :]')
            dt = [int(s) for s in regex.split(mqttclient.mqtt_result['sma_time'])]
            dt.insert(3, 0)       # add day of the week
            dt.append(0)            
            rtc.datetime(tuple(dt))
    
    time.sleep(1)
    if "update" in mqttclient.mqtt_result and mqttclient.mqtt_result['update'] != 'run':
        updates.do(mqttclient, mqttclient.mqtt_result)   
    else:
        print('no update found')

    mqttclient.mqtt.publish(config.Topic, b'run')
    time.sleep(1)

    if True:
        mqttclient.mqtt.publish(config.Topic, b'sleep')
        time.sleep(1)
        mqttclient.disconnect()
        t = rtc.datetime()
        mqttclient.mqtt_result['last_time'] = f'{t[2]:02d}.{t[1]:02d}.{t[0]:04d} {t[4]:02d}:{t[5]:02d}:{t[6]:02d}'
        tiles.dvar = mqttclient.mqtt_result                 # get all variables from mqtt
        ssd.init()
        led.off()                
        tiles.tiles2display(ssd, ssdred)         # calculate the titles
        tiles.text2display(ssd, ssdred)
        tiles.lines2display(ssd)
        ssdred.show()
        ssd.show()
        machine.freq(20_000_000)        
        ssd.sleep()
        gc.collect()
        print(f"update done {mqttclient.mqtt_result['last_time']}")
        print(f"  next update: {config.epaper_update}s")        

        # TODO enable sleep mode for the RP2040
        time.sleep(config.epaper_update)
        #machine.lightsleep(20000)     # does not work :-( with MicroPython > v1.23
        machine.freq(125_000_000)
    else:
        break
