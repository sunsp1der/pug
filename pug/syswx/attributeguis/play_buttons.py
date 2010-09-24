"""play_buttons.py"""
from inspect import isroutine

import wx
import wx.lib.buttons as buttons


from pug.syswx.wxconstants import *
from pug.syswx.util import show_exception_dialog
from pug.syswx.attributeguis.base import Base
from pug.syswx.agui_label_sizer import AguiLabelSizer
from pug.util import get_image_path

class PlayButtons (Base):
    """An attribute gui with Rewind, Play, Pause, Stop, FastForward buttons

PlayButtons(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugWindow. 
aguidata: {
    'rewind': the function to run on Rewind press
    'play': the function to run on Play press
    'pause': the function to run on Pause press
    'stop': the function to run on Stop press
    'fast_forward': the function to run on Fast Forward press
    'execute': the function to run on Execute press
    }
    
    If functions are not defined, button will not be shown.
    If functions are strings, they will be converted to methods of the object 
        being viewed.
For kwargs arguments, see the Base attribute GUI
"""
    playbutton = None
    pausebutton = None
    
    def __init__(self, attribute, window, aguidata ={}, **kwargs):
        #widgets
        control = wx.Panel(window, 
                           size=(1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1, WX_STANDARD_HEIGHT))
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        control.SetSizer(controlSizer)

        try:
            rewind_image = wx.Bitmap(get_image_path("rewind.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            rewind_image = wx.ArtProvider.GetBitmap(wx.ART_UNDO,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)                             
        try:
            play_image = wx.Bitmap(get_image_path("play.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            play_image = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)                             
        try:
            pause_image = wx.Bitmap(get_image_path("pause.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            pause_image = wx.ArtProvider.GetBitmap(wx.ART_WARNING,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)                                         
        try:
            stop_image = wx.Bitmap(get_image_path("stop.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            stop_image = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)                             
        try:
            execute_image = wx.Bitmap(get_image_path("execute.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            execute_image = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
        try:
            fast_forward_image = wx.Bitmap(get_image_path("fast_forward.png"), 
                                              wx.BITMAP_TYPE_PNG)
        except:
            fast_forward_image = wx.ArtProvider.GetBitmap(wx.ART_REDO,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)                                         
        
        buttonOrder = ['rewind', 'play', 'pause', 'stop', 'fast_forward', 
                       'execute']
        infoDict = {
                'rewind':('Rewind', rewind_image),
                'play':('Play', play_image),
                'pause':('Pause', pause_image),
                'stop':('Stop', stop_image),
                'fast_forward':('Fast Forward', fast_forward_image),
                'execute':('Execute in separate process', execute_image),
                }
        self.functionDict = {}
        self.buttonDict = {}
        
        for item in buttonOrder:
            info = infoDict[item]
            self.buttonDict[item] = None
            if not aguidata.has_key(item):
                continue
            if isroutine(aguidata[item]):
                func = aguidata[item]
            else:
                func = getattr( window.object, aguidata[item], None)
                if not isroutine(func):
                    continue
            if item == 'play':
                button = buttons.ThemedGenBitmapToggleButton(control, -1, None,
                                                   size=WX_BUTTON_SIZE)
                self.playbutton = button
            elif item == 'pause':
                button = buttons.ThemedGenBitmapToggleButton(control, -1, None,
                                                   size=WX_BUTTON_SIZE)
                self.pausebutton = button
                button.Enable(False)
            else:
                button = buttons.ThemedGenBitmapButton(control, -1, None,
                                                   size=WX_BUTTON_SIZE)
            button.type = item
            self.buttonDict[item] = button
#            print info[1].Ok(), info[1]
            button.SetBitmapLabel(info[1])
            self.functionDict[button] = func    
            button.SetToolTipString(info[0])
            control.Bind(wx.EVT_BUTTON, self.button_press, button)
            controlSizer.Add( button)
        line = AguiLabelSizer(control, ' ')
        controlSizer.Add(line, 1, wx.EXPAND)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs) 
        
    def setup(self, attribute, window, aguidata):
        if self.aguidata != aguidata:
            self.control.Destroy()
            self.label.Destroy()
            self.__init__(attribute, window, aguidata)
            return
        else:
            Base.setup( self, attribute, window, aguidata)        
        
    def button_press(self, event=None, button=None):  
        """Call the appropriate function"""
        try:
            if event:
                button = event.GetEventObject()
            elif button is None:
                return
            else:
                button = self.buttonDict[button]
            retvalue = self.functionDict[button]()
            if button.type == 'play' and retvalue == True:
                button.Enable(False)
                if self.buttonDict['pause']:
                    self.buttonDict['pause'].Enable(True)
            if button.type == 'stop':
                if self.buttonDict['play']:
                    self.buttonDict['play'].Enable(True)
                    self.buttonDict['play'].SetValue(False)
                if self.buttonDict['pause']:
                    self.buttonDict['pause'].SetValue(False)
                    self.buttonDict['pause'].Enable(False)
        except:
            show_exception_dialog(self.control)
            try:
                wx.EndBusyCursor()
            except:
                pass
        self.refresh_window()
