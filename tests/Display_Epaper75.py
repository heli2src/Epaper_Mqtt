
import os
import time
import framebuf
from color_setup import ssd
from color_setup import ssdred

from gui.core.writer import Writer
from gui.core.nanogui import refresh
from gui.widgets.meter import Meter
from gui.widgets.label import Label

# Fonts
# import gui.fonts.arial10 as small
#import gui.fonts.ezFBfont_timB10_ascii_14 as small
import gui.fonts.ezFBfont_timB14_full_21 as tfont

from wlanmqtt import WlanMqtt
import config


class Tiles():
    """
    A tile consists of a heading, an icon and the measured value.

    """

    def __init__(self, imagepath='/images', ):
        self.imagepath = imagepath
        self.dvar = []

    def image_load(self, fn):
        try:
            with open(fn, "rb") as f:
                f.readline()    # Magic number
                f.readline()    # Creator comment
                dim = f.readline()[:-1]
                w, h = dim.split(' ') if type(dim) is str else dim.decode('ascii').split(' ')   # Dimensions
                data = bytearray(f.read())
            w = int(w)
            h = int(h)
            fbuf = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
            return fbuf, w, h
        except Exception:
            print(f'{fn} not found')
            return None, 0, 0

    def read_icon(self, title, sub):
        fbuf, w, h, = self.image_load(f"{self.imagepath}/{sub['c'][0]}.pbm")
        return fbuf, w, h

    def create_tiles(self, dictionary):
        for title in dictionary:
            dictionary[title]['c'] = self.read_icon(title, dictionary[title])     # TODO: for memeory reason it should be better, read the image for each placement
        self.content = dictionary
        
    def transfer2display(self, display1, display2=None):
        font = tfont
        wri1 = Writer(display1, font, verbose=False)
        if display2 is not None:
            wri2 = Writer(display2, font, verbose=False)
        for tile in self.content:
            xy = self.content[tile]['p']
            wh = self.content[tile]['c'][1], self.content[tile]['c'][2]
            display1.blit(self.content[tile]['c'][0], xy[0], xy[1])
            
            Label(wri1, xy[1]-15, xy[0], wh[0], align=2).value(tile)    # y, x
            update1 = True         # TODO calculate if update necessary
            update2 = False
            dh = 0            
            for var in self.content[tile]['v']:
                var = str(self.dvar[var]) if var in self.dvar else 'n.f.'
                Label(wri1, xy[1]+wh[1]-10+dh, xy[0], wh[0], align=2).value(var)
                dh += font.height()
                
            #print(tile, xy, wh)
        return update1, update2


# clear display:
clear= False
ssd.fill(0)          # auf White setzen
ssdred.fill(0)       # auf White setzen

ssdred.show()
if clear:    
    ssd.show()

mqttclient = WlanMqtt(config.SERVER, wlSsid=config.WlSsid, wlPw=config.WlPw)
mqttclient.init(config.TOPICS)

tiles = Tiles()
tiles.create_tiles(config.TILES)
lasttime = time.time() - config.epaper_update + 10         # wait 10s to get the first mqtt values

while True:
    mqttclient.mqtt.wait_msg()
    
    # TODO enable sleep mode for the RP2040
    if time.time()-lasttime > config.epaper_update:
        tiles.dvar = mqttclient.mqtt_result                 # get all variables from mqtt
        ssd.init()
        upd1, upd2 = tiles.transfer2display(ssd, ssdred)    # calculate the page
        ssdred.show()
        ssd.show()
        ssd.sleep()
        lasttime = time.time()
    
    








