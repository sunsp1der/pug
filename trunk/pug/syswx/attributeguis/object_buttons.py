import re
import weakref

import wx

from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base
from pug.syswx.pugbutton import PugButton
from pug.syswx.agui_label_sizer import AguiLabelSizer

class ObjectButtons (Base):
    """An attribute gui that lets the user open pug windows to view an object

ObjectButtons(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame. 
aguidata: {
    'viewButton': if True, show viewButton (see below)... default is true
    'newViewButton': if True, show newViewButton (see below)... default is true
    }
For kwargs arguments, see the Base attribute GUI

Contains text showing attribute's value and two buttons... 
    viewButton: changes the parent window to display this object
    newViewButton: opens a new pug window to display objet
    
This control is generally meant to be used for instances, but could be used for
any object.
"""
    viewButton = newViewButton = 0
    def __init__(self, attribute, frame, aguidata ={}, **kwargs):
        aguidata.setdefault('viewButton',False)#,True)
        aguidata.setdefault('newViewButton',True)        
        #widgets
        control = wx.Panel(frame.get_control_window(), 
                           size=(1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        obj = getattr(frame.object,attribute)
        control.value = ''
        
        if aguidata['newViewButton']:
            newViewButton = PugButton(control, obj,
                                   True, attribute, frame)
            controlSizer.Add(newViewButton)
            self.newViewButton = newViewButton    
            self.newViewButton.Bind(wx.EVT_BUTTON, self.evt_view)     

        if aguidata['viewButton']:
            viewButton = PugButton(control, obj,
                                   False, attribute, frame)
            self.viewButton = viewButton
            controlSizer.Add(viewButton)
            self.viewButton.Bind(wx.EVT_BUTTON, self.evt_view)     
        
        textSizer = AguiLabelSizer(control)
        infoText = textSizer.text
        self.infoText = infoText
        self.textSizer = textSizer

        # sizers
        control.SetSizer(controlSizer)
        controlSizer.AddSpacer((3,3))        
        controlSizer.AddSizer(textSizer,1,wx.EXPAND)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, frame, aguidata, **kwargs)
        
    def evt_view(self, event):
        self.setup_buttons(self.get_control_value())  
        event.Skip()
        
    def setup_buttons(self, obj):
        for button in [self.viewButton, self.newViewButton]:
            if button:
                button.set_object(obj, self.attribute, self._window)
        
    def set_control_value(self, obj):
        if hasattr(obj,'gname') and obj.gname:
            text = obj.gname
        else:
            text = type(obj).__name__
            if text == 'type':
                text = str(obj)
        self.infoText.SetLabel(text)
        self.control.value = obj
        
    def get_control_value(self):
       return self.control.value
   
                
