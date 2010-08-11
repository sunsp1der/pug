"experimental app for use with pig. NOT CURRENTLY USED"
import wx

from pug import App
from pig.PigDirector import PigDirector

class PigApp( App):
    def OnInit(self):
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        App.OnInit(self)
        return True
#    
    def OnIdle(self, event=None):
        try:
            PigDirector.tick()
            event.RequestMore()
        except:
            pass
    
    def OnKey(self, event=None):
        print "k"