import re

import wx

from pug.util import get_type_name
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
    'view_button': if True, show view_button (see below). default: False
    'new_view_button': if True, show new_view_button (see below). default: True
    }
For kwargs arguments, see the Base attribute GUI

Contains text showing attribute's value and two buttons... 
    view_button: changes the parent window to display this object
    new_view_button: opens a new pug window to display objet
    
This control is generally meant to be used for instances, but could be used for
any object.
"""
    view_button = new_view_button = 0
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        aguidata.setdefault('view_button',False)#,True)
        aguidata.setdefault('new_view_button',True)        
        #widgets
        control = wx.Panel(window, size=(1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        obj = getattr(window.object,attribute)
        control.value = obj
        
        if aguidata['new_view_button']:
            new_view_button = PugButton(control, obj,
                                   True, attribute, window)
            controlSizer.Add(new_view_button)
            self.new_view_button = new_view_button    
            self.new_view_button.Bind(wx.EVT_BUTTON, self.evt_view)
        elif self.new_view_button:
            self.new_view_button.Destroy()     

        if aguidata['view_button']:
            view_button = PugButton(control, obj,
                                   False, attribute, window)
            self.view_button = view_button
            controlSizer.Add(view_button)
            self.view_button.Bind(wx.EVT_BUTTON, self.evt_view) 
        elif self.view_button:
            self.view_button.Destroy()     
        
        textSizer = AguiLabelSizer(control)
        infoText = textSizer.textCtrl
        self.infoText = infoText
        self.textSizer = textSizer

        # sizers
        control.SetSizer(controlSizer)
        controlSizer.AddSpacer((3,3))        
        controlSizer.AddSizer(textSizer,1,wx.EXPAND)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        if aguidata != self.aguidata:
            self.__init__( attribute, window, aguidata)
            return
        else:
            self.setup_buttons( window.object)
            self.set_control_value( window.object)
            Base.setup( self, attribute, window, aguidata)
        
    def evt_view(self, event):
        self.setup_buttons(self.get_control_value())  
        event.Skip()
        
    def setup_buttons(self, obj):
        for button in [self.view_button, self.new_view_button]:
            if button:
                button.set_object(obj, self.attribute, self.window)
        
    def set_control_value(self, obj):
        text = self.label_text(obj)
        self.infoText.SetLabel(text)
        self.infoText.SetToolTipString(repr(obj))
        self.control.value = obj

    def label_text(self, obj):
        if hasattr(obj,'gname') and obj.gname and obj.gname == str(obj.gname):
            text = obj.gname
        else:
            text = get_type_name(obj)
            if text == 'type':
                text = str(obj)
        return text
    
    def refresh(self, event=None):
        Base.refresh(self, event)
        self.set_control_value(self.control.value)
        
    def get_control_value(self):
       return self.control.value
   
                
