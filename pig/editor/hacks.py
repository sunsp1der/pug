"""hacks.py

This file contains changes and fixes for Opioid2D that needed to be hacked in.
"""
import Opioid2D
from Opioid2D.public.Image import ImageInstance
from Opioid2D.internal import textures
import Opioid2D.internal.bitmap_transform as transform

import cOpioid2D as _c

#hack for making Opioid2D.Vector objects more visible
__old_repr = Opioid2D.Vector.__repr__
def __vect_repr(self):
    #old = __old_repr(self)
    return ''.join(['(', str(self.x), ', ', str(self.y),') - Opioid Vector'])     

Opioid2D.Vector.__repr__ = __vect_repr

#hack to fix problem with large textures
TEXSIZE = 1024
class TextureSheet(object):
    
    def __init__(self):
        global TEXSIZE
        self.TEXSIZE = TEXSIZE
        self._tex = _c.Texture(self.TEXSIZE)

        self.y = 0
        self.next_y = 0
        self.x = 0

    def insert_image(self, w, h, data, border=0):
        if self.x + w <= self.TEXSIZE:
            if  self.y + h > self.TEXSIZE:
                return None
            x = self.x
            y = self.y
        else:
            if self.next_y + h <= self.TEXSIZE:
                x = 0
                y = self.next_y
            else:
                return None
        if y != self.y:
            self.y = y
        self.x = x + w
        if self.y + h > self.next_y:
            self.next_y = self.y + h
        self._tex.WriteBytes(x,y,w,h,data)
        ts = float(self.TEXSIZE)
        return _c.Image(self._tex, w-border*2, h-border*2, (x+border)/ts, (y+border)/ts, (x+w-border)/ts, (y+h-border)/ts)
textures.TextureSheet = TextureSheet
#print "hacked"
    
# Grid Image just doesn't work right.
def _create_image( bmp, hotspot=None, border=1):
    # skip this first clause...
#    if bmp.width+border*2 > 512 or bmp.height+border*2 > 512:
#        img = GridImage(bmp, border=border)
#    else:
    self = Opioid2D.ResourceManager
    if border:
        bmp = bmp.transform(transform.make_bordered, border)
    img = self._texmgr.add_image(bmp, border)
    img = ImageInstance(img)
    if hotspot:
        img._cObj.hotspot.set(*hotspot)
    return img

Opioid2D.ResourceManager._create_image = _create_image
