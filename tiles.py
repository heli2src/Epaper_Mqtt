# Released under the MIT license see LICENSE
import gc
import framebuf
from gui.core.writer import Writer
# from gui.core.nanogui import refresh
# from gui.widgets.meter import Meter
from gui.widgets.label import Label
import gui.fonts.ezFBfont_timB14_full_21 as tfont21


class Tiles():
    """
    A tile consists of a heading, an icon and the measured value.

    """

    def __init__(self, content, imagepath='/images'):
        self.imagepath = imagepath
        self.content = content
        self.dvar = []
        gc.enable()
        self.loadimg = True

    def image_load(self, fn, loadimg= True):
        # print(f'load {fn}, alloc mem={gc.mem_alloc()}')
        w = 0
        h = 0
        data = None
        try:
            with open(fn, "rb") as f:
                f.readline()    # Magic number
                f.readline()    # Creator comment
                dim = f.readline()[:-1]
                w, h = dim.split(' ') if type(dim) is str else dim.decode('ascii').split(' ')    # Dimensions
                data = bytearray(f.read()) if loadimg else None
            w = int(w)
            h = int(h)
            fbuf = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB) if data is not None else 0
            print(f'load {fn} ({w}, {h})')
        except Exception as ex:
            print(f'load {fn} with exception {ex}')
            w = int(w)
            h = int(h)            
            fbuf = None
        return fbuf, w, h        

    def tiles2display(self, display1, display2=None):
        content = self.content["tiles"]
        for tile in content:
            font = content[tile]['c'][1]
            wri1 = Writer(display1, font, verbose=False)
            if display2 is not None:
                wri2 = Writer(display2, font, verbose=False)
            gc.collect()
            img, w, h, = self.image_load(f"{self.imagepath}/{content[tile]['c'][0]}.pbm", self.loadimg)
            xy = content[tile]['p']
            if img is not None and type(img) is not int:                
                display1.blit(img, xy[0], xy[1])
            elif img is None:
                Label(wri1, xy[1] + (h//2), xy[0], 50, align=2).value('img error')
            img = None
            
            if len(tile) > 1:
                Label(wri1, xy[1]-15, xy[0], w, align=2).value(tile)    # y, x                
            dh = 0
            dvalues = content[tile]['v'] if 'v' in content[tile] else content[tile]['h']
            for var in dvalues:
                var = str(self.dvar[var]) if var in self.dvar else 'n.f.'
                if 'v' in content[tile]:
                    Label(wri1, xy[1]+h-10+dh, xy[0], w, align=2).value(var)
                else:
                    Label(wri1, xy[1]+font.height()+dh, xy[0]+w-10, wri1.stringlen(var), align=1).value(var)
                dh += font.height()
        self.loadimg = False              # load only images after startup
        return
    
    def text2display(self, display1, display2=None):
        content = self.content["text"]
        for text in content:
            font = content[text]['c'][0]
            wri1 = Writer(display1, font, verbose=False)
            if display2 is not None:
                wri2 = Writer(display2, font, verbose=False)
            xy = content[text]['p']
            h = font.height()
            w = wri1.stringlen(text)
            Label(wri1, xy[1], xy[0], w, align=2).value(text)
            dh = 0
            for var in content[text]['v']:
                var = str(self.dvar[var]) if var in self.dvar else 'n.f.'                
                Label(wri1, xy[1]+dh, xy[0]+w, wri1.stringlen(var), align=2).value(var)
                dh += font.height()
                
    def lines2display(self, display1):
        content = self.content["lines"]
        for line in content:
            for w in range(0, line[4]):
                if line[0] == line[2]:
                    display1.hline(line[0], line[1]+w, line[3]-line[1], 1)
                else:
                    display1.hline(line[0]+w, line[1], line[2]-line[0], 1)
                    
    def printf(self, text, display, x=150, y= 200, font=tfont21):
        wr = Writer(display, font, verbose=False)
        for t in text.split('\n'):
            Label(wr, y, 150, wr.stringlen(t)).value(t)
            y += 30


if __name__ == "__main__":
    from color_setup import ssd
    from color_setup import ssdred
    import config

    ssd.fill(0)          # auf White setzen
    ssdred.fill(0)       # auf White setzen

    ssdred.show()

    tiles = Tiles(config.CONTENT)
    
    tiles.tiles2display(ssd, ssdred)
    tiles.text2display(ssd, ssdred)
    tiles.lines2display(ssd)
    tiles.printf("This is a text\nline 1\nline2", ssdred, y=10)
    ssdred.show()
    ssd.show()
