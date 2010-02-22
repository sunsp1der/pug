import Opioid2D

class PigState( Opioid2D.State):
    def enter(self):
        self.busy = False
        self.exitted = False
        self.originalCursor = Opioid2D.Mouse.cursor
        
    def exit(self):
        self.exitted = True

    def on_set_busy_state(self, On=True):
        if On:
            Opioid2D.Mouse.cursor = _busyCursor
        else:
            Opioid2D.Mouse.cursor = self.originalCursor
        self.busy = On
        
strings = [" XXXXXXXXXXXXXX ",
           " XOOOOOOOOOOOOX ",
           " XOXXXXXXXXXXOX ",
           "  XOXOOOOOOXOX  ",
           "   XOXOOOOXOX   ",
           "   XOXXXXXXOX   ",
           "    XOXXXXOX    ",
           "     XOXXOX     ",
           "     XOXXOX     ",
           "    XOXOOXOX    ",
           "   XOXOOOOXOX   ",
           "   XOXOXXOXOX   ",
           "  XOXXXXXXXXOX  ",
           " XOXXXXXXXXXXOX ",
           " XOOOOOOOOOOOOX ",
           " XXXXXXXXXXXXXX "]

_busyCursor = Opioid2D.HWCursor.compile(strings=strings, hotspot = (8,8),
                                        white='O',black='X',xor='@')        