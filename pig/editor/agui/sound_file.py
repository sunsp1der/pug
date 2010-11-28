from time import sleep

import wx
import wx.lib.buttons as buttons

import Opioid2D

from pug import Filename
from pug.util import get_image_path
from pug.syswx.wxconstants import *

from pig.audio import get_sound

class SoundFile( Filename):
    def __init__(self, attribute, window, aguidata={}, **kw):
        aguidata['wildcards'] = "wav file (*.wav)|*.wav" \
                   "|ogg file (*.ogg)|*.ogg|" 
#                   "mp3 file (*.mp3)|*.mp3|" \
#                   "midi files (*.mid)|*.mid|" \
#                   "All files (*.*)|*.*"
        aguidata['subfolder'] = "sound"
        Filename.__init__(self, attribute, window, aguidata=aguidata, **kw)
        # play sound button
        try:
            play_image = wx.Bitmap(get_image_path("play.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            play_image = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)                             

        playbutton = buttons.ThemedGenBitmapButton(self.control, 
                                                   bitmap=play_image, 
                                                   size=WX_BUTTON_SIZE)
        playbutton.SetToolTipString('Play sound. Hold to loop.')
        playbutton.Bind(wx.EVT_LEFT_DOWN, self.play)
        playbutton.Bind(wx.EVT_LEFT_UP, self.stop)
        self.control.GetSizer().Add(playbutton,0)
        self.sound = None # currently playing sound
        
    def play(self, event):
        from pygame import mixer
        if not mixer.get_init():
            mixer.init()
        if mixer.get_busy() and self.sound:
            self.sound.stop()
            return
        volume_attr = self.aguidata.get('volume')
        if volume_attr:
            volume = getattr(self.window.object, volume_attr)
        else:
            volume = 1
        try:
            sound = get_sound( self.get_control_value(), volume=volume)
            sound.play()
            self.sound = sound
        except:
            self.sound = None
        self.play_button_down = True
        self.looping = False
        wx.CallLater( 0.1, self.test_button)
        event.Skip()
                
    def test_button(self):
        "test to see if button is being held down"
        if self.sound is None:
            return
        from pygame import mixer
        if self.play_button_down:
            if mixer.get_busy():
                wx.CallLater( 0.1, self.test_button)
            else:
                self.looping = True
                (Opioid2D.Delay(0) + \
                            Opioid2D.CallFunc(self.sound.play,loops=-1)).do()
                wx.CallLater( 0.1, self.test_button)
        elif self.looping:
            self.sound.stop()   
        
    def stop(self, event):
        self.play_button_down = False
        event.Skip()