#!/usr/bin/env python

"""
Copyright (C) 2007 John Popplewell

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Contact : John Popplewell
Email   : john@johnnypops.demon.co.uk
Web     : http://www.johnnypops.demon.co.uk/python/

If you have any bug-fixes, enhancements or suggestions regarding this 
software, please contact me at the above email address.

$RCSfile: resizedemo.py,v $
$Id: resizedemo.py,v 1.2 2007/10/21 22:36:01 jfp Exp $
"""

import pygame

from pygame.locals  import *
from wm_ext.appwnd import AppWnd


class Demo(AppWnd):
    TIMER_EVENT = USEREVENT+1

    def __init__(self, noframe, alwaysontop):
        opts = self.getDefaultOptions()
        opts.frame = not noframe
        opts.alwaysontop = alwaysontop
        self.move_start = None
        self.outline = 0
        AppWnd.__init__(self, opts)
        self.init("Resizing Demo")

    def SetPosition(self, preset):
        x, y = self.preset2pos(preset)
        self.SetWindowPosition((x, y))

    def doExpose(self):
        size = self.screen_size
        self.screen.fill((80, 0, 0))
        self.screen.fill((255, 255, 0), pygame.Rect(0, 0, size[0]-1, 1))
        self.screen.fill((255, 255, 0), pygame.Rect(0, size[1]-1, size[0], 1))
        self.screen.fill((255, 255, 0), pygame.Rect(0, 0, 1, size[1]-1))
        self.screen.fill((255, 255, 0), pygame.Rect(size[0]-1, 0, 1, size[1]))
        pygame.display.flip()

    def doResize(self, size):
        self.doExpose()

    def doEvent(self, event):
        if event.type == self.TIMER_EVENT:
            if self.IsMaximized():
                self.Restore()
            else:
                self.Maximize()
        elif event.type in (KEYUP, KEYDOWN):
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                     return 1
                elif event.key == K_o:
                    if self.outline:
                        self.ClearWindowShape()
                        self.outline = 0
                    else:
                        cross = ((300, 0), (340, 0), (340, 220), (640, 220), (640, 260), 
                                 (340, 260), (340, 640), (300, 640), (300, 260), (0, 260), 
                                 (0, 220), (300, 220))
                        self.SetWindowShapePolygon(cross)
                        self.outline = 1
                elif event.key == K_i:
                    self.Minimize()
                elif event.key == K_m:
                    if self.IsMaximized():
                        self.Restore()
                    else:
                        self.Maximize()
                elif event.key == K_t:
                    pygame.time.set_timer(self.TIMER_EVENT, 500)
                elif event.key == K_s:
                    pygame.time.set_timer(self.TIMER_EVENT, 0)
                elif event.key == K_RETURN and event.mod & KMOD_ALT:
                    self.toggleFullscreen()
                elif event.key >= K_KP1 and event.key <= K_KP9:
                    self.SetPosition(event.key-K_KP1+1)
        elif event.type == MOUSEBUTTONDOWN:
            if not self.IsMaximized() and event.button == 1:
                self.move_start = self.Client2Screen(event.pos)
                self.move_orig  = self.GetWindowPosition()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.move_start = None
        elif event.type == MOUSEMOTION:
            if self.move_start:
                pos = self.Client2Screen(event.pos)
                x = self.move_orig[0] + (pos[0] - self.move_start[0])
                y = self.move_orig[1] + (pos[1] - self.move_start[1])
                self.SetWindowPosition((x, y))
        return 0


from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--noframe",action="store_true", dest="noframe", default=False, help="create window with no furniture")
    parser.add_option("--alwaysontop",action="store_true", dest="alwaysontop", default=False, help="keep window on top of others")
    opts, args = parser.parse_args()
    app = Demo(opts.noframe, opts.alwaysontop)
    app.run()
    app.quit()

