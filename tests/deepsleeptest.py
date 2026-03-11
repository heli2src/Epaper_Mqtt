import machine
import time


led = machine.Pin('LED', machine.Pin.OUT, value=0)    # Status LED

while True:
    led.on()
    time.sleep(.1)
    led.off()
    machine.deepsleep(500)
    #time.sleep(.5)    