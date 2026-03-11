# Released under the MIT license see LICENSE

import time
import os
import machine


class Update():
    """

    comands in messages['update']:
        run                     # continue running programm
        dir
        closefile
        openfile:{name}
        reset
        rmfile:{name}        
        wait
        writefile               # if you write more than once, than use the 'wait' command and than writefile again
    """
    
    def __init__(self, led, state_topic):
        self.led = led
        self.state_topic = state_topic
        self.messages = None
        
    def do(self, mqttclient, messages):
        self.messages = messages
        self.led.on()
        self.mqttclient = mqttclient
        lastcmd = ""
        file = None
        print(f"messages['update'] = {messages['update']}")
        while messages['update'] != 'run':
            while mqttclient.mqtt.check_msg():
                mqttclient.mqtt.wait_msg()

            cmd = messages['update']
            if type(cmd) is not str:
                break
            cmd = cmd.split('\n')
            if cmd[0] != lastcmd and lastcmd.find('=') < 0:
                try:
                    if cmd[0].find("closefile") == 0:                # close file      
                        file.close()
                        file = None
                    elif cmd[0].find("dir") == 0:                      # list directory
                        cmd = [f"dir={os.listdir()}"]
                    elif cmd[0].find("openfile:") == 0:                # open file for write
                        # filename = cmd[0].split(':')[1].strip()
                        file = open(cmd[0].split(':')[1].strip(), "w")
                    elif cmd[0].find("reset") == 0:
                        machine.reset()
                    elif cmd[0].find("rmfile:") == 0:                # remove file
                        os.remove(cmd[0].split(':')[1])
                    elif cmd[0].find("wait") == 0:                   # wait for next command
                        pass                
                    elif cmd[0].find("writefile") == 0:              # write message to file
                        print(f"write to file {file}\n{messages['update'].encode('utf-8')}")
                        for line in cmd[1:]:
                            file.write(f"{line}\n")
                            print(line.encode('utf-8'))
                    else:
                        cmd = [f"{cmd[0]}= command not found"]
                except Exception as e:
                    cmd = [f"{cmd[0]}= Exception: {e}"]
                print(cmd[0])
                self.lastcmd = cmd[0]
                self.state(cmd[0])
            lastcmd = cmd[0]
            time.sleep(1)
            self.led.toggle()
        if file is not None:
            file.close()
        self.led.off()
        
    def state(self, msg):
        self.mqttclient.mqtt.publish(self.state_topic, f"update_loop:{msg}")
        