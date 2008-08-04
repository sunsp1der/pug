"""Base class for attribute guis"""
import time

import wx

from pug.constants import *
from pug.syswx.helpframe import HelpFrame
from pug.syswx.wxconstants import *
from pug.syswx.agui_label_sizer import AguiLabelSizer

class Base():
    """Base attribute gui contains label code and other automated features
    
(self, attribute, window, aguidata = None, control_widget = None, 
    label_widget = None)
attribute: the attribute this control deals with
frame: the window parent (a wxWindow). frame.object is the viewed object.
aguidata: dictionary of special agui information. Can be customized for specific
    agui types, but these keys work for all aguis derived from Base:
        'label': the label string
        'read_only': attribute cannot be edited via gui
        'control_only': hide label_widget and give control_widget the full area
        'tooltip': the tooltip that will pop up on the label
        'background_color': for label_widget and control_widget call 
            'SetBackgroundColor' with this value
        'growable': if true, this allows the control to grow vertically
control_widget: the widget used for input, usually defined by derived classes. 
label_widget: custom wxWidget label, can be defined by derived classes.

Attribute guis should almost always be derived from Base. Base.label is the
label displayed on the left of a pugFrame. Base.control is the control displayed
on the right of a pugFrame.

The main functions that attribute guis are meant to over-ride are:
set_control_value(self, val): make Base.control display val
get_control_value(self): return the value shown in Base.control

Override these if get_control_value does not return the attribute's actual 
value...
set_attribute_value(self): apply the control's value to Base.attribute. 
    return True if successfully applied
get_attribute_value(self, event=None): get the attribute's value, and return it
    converted to the format that get_control_value and set_control_value use

Note that set_control_value should always accept data in the same form that
get_control_value and get_attribute_value return it. Likewise, get_control_value
should return data in the same form the set_control_value and 
set_attribute_value expect it.
"""
    def __init__(self, attribute, window, aguidata = {}, control_widget = None, 
                 label_widget = None, **kwargs):
        if attribute is None:
            attribute = ''
        self._window = window
        self.attribute = attribute
        self._aguidata = aguidata
        try:
            value = getattr(window.object, attribute, None)
        except:
            value = None
        # control
        if control_widget:
            self.control = control_widget
        else:
            # no control provided, so just make an empty panel
            self.control = wx.Panel(window.get_label_window(), 
                                    size = (1,WX_STANDARD_HEIGHT))
        self.readonly = aguidata.get('read_only',False)
            
        # label    
        labelText = aguidata.get('label', 
                                 ''.join([PUGFRAME_ATTRIBUTE_PREFIX,attribute]))
        if label_widget:
            self.label = label_widget
        elif labelText != None:
            #panel
            label = wx.Panel(window.get_label_window(), style=0,
                             size=(0, self.control.Size[1]))
            #label
            textSizer = AguiLabelSizer(label, labelText)
            label.SetSizer(textSizer)
            label.text = textSizer.text
            # label.sizer = textSizer
            # label.preferredWidth = textSizer.preferredWidth # FOR SASH
            self.label = label
            #self.label.SetMinSize((-1,self.control.Size[1]))
        else:
            # no label info, just make an empty frame
            self.label = wx.Panel(window.get_label_window(), style=0,
                             size=(0, self.control.Size[1]))
            #self.label.SetMinSize((-1,self.control.Size[1]))
        
        self.tooltip = None
        if aguidata.has_key('tooltip'):
            self.tooltip = aguidata['tooltip']
        else:
            try: # check if this is a property
                prop = getattr(self._window.object.__class__, 
                               attribute, None)
                if type(prop) == property:
                    self.tooltip = prop.__doc__
            except:
                pass
        if self.tooltip and hasattr(self.label, 'text'):
            self.label.text.SetToolTipString(self.tooltip) 
        else:
            self.doc_to_tooltip()           
            
        self.match_control_size()
            
        #background color
        if aguidata.has_key('background_color'):
            backgroundColor = aguidata['background_color']
            try:
                self.label.SetBackgroundColour(backgroundColor)
                self.control.SetBackgroundColour(backgroundColor)
            except:
                pass
                            
        # context help
        self.setup_context_help(self.label, window)
        self.setup_context_help(self.control, window)
        
        # these will be shown again when placed in pugwindow panels
        self.label.Hide()
        self.control.Hide()
        
        # FOR SASH
        # make sure label has a preferredWidth attribute
        # if not hasattr(self.label,'preferredWidth'):
        #    label.preferredWidth = 0
            
        
    def get_control_value(self):
        """get the value of the attribute - defined by derivative classes

By default, this returns the attribute value        
"""
        return getattr(self._window.object, self.attribute, None)
    
    def set_control_value(self, value):
        """set the value of the attribute - defined by derivative classes"""
        return
        
    def refresh(self, event=None):
        """Get value from object"""
        value = self.get_attribute_value()
        control_value = self.get_control_value()
        if value != control_value:
            #only set if necessary
            self.set_control_value(value)
            if not self.tooltip:
                self.doc_to_tooltip()

    def doc_to_tooltip(self):
        doc = ''
        value = self.get_attribute_value()
        if value.__class__ not in BASIC_TYPES:
            doc = getattr(value,'__doc__','')
        elif value is not None:
            try:
                doc = type(value).__name__
            except:
                pass   
        try:
            self.label.text.SetToolTipString(doc)
        except:
            if hasattr(self.label, 'text'):
                if self.label.text.GetToolTip():
                    self.label.text.SetToolTipString(' ')
        
    def get_attribute_value(self):
        return getattr(self._window.object, self.attribute, None)
 
    def apply(self, event = None):
        """Apply change to object
        
When auto apply is off, skip apply events that were created by the event system        
"""
        # when auto apply is off, skip apply events that were created by the 
        # event system
        if not self._window.settings['auto_apply'] and event:
            return False
        # see if we even need to do anything
        try:
            control_value = self.get_control_value()
        except:
            return False
        attribute_value = self.get_attribute_value()
        if attribute_value == control_value:
            # no need to set... effectively, our work is done successfully
            return True
        # we need to set, but make sure attribute is not readonly
        if self.readonly:
            retDlg = wx.MessageDialog(self.control, 
                              ''.join([self.attribute,
                                       ' cannot be editted via gui']), 
                               'Read Only', wx.OK)
            retDlg.ShowModal()       
            applied = False   
        else:                
            applied = self.set_attribute_value()
        if applied:
            starttime = time.time()
            while self.get_attribute_value() != control_value:                
                # sometimes we have to wait a bit for it to take effect
                # if this takes more than 3 seconds, forget it
                time.sleep(0.01)
                if time.time() - starttime > 3: 
                    applied = False
                    break
            self.refresh_window()        
            self.set_control_value(self.get_control_value())          
        else:
            # bad apply... just revert
            self.refresh()  
        return applied

    def set_attribute_value(self):
        """set_attribute_value()->False if there was a problem. True otherwise.
        
Try to set the aguis attribute to the value shown in the control
"""
        try:
            control_value = self.get_control_value()
            attribute_value = self.get_attribute_value()
        except:
            return False
        if attribute_value is None: 
            # attribute type not set
            try:
                 setattr(self._window.object,self.attribute,control_value)
            except:
                return False
            else:
                return True                  
        else:
            try:
                # if we have a basic attribute type, and we're not setting 
                # to None, typecast our control_value to the attribute 
                # value's current type
                if type(attribute_value) in BASIC_TYPES and \
                                                    control_value is not None:
                    typedValue = type(attribute_value)(control_value)
                else:
                    # no type-casting for special types... don't want any 
                    # weird garbage sitting around
                    typedValue = control_value
                setattr(self._window.object, self.attribute, typedValue)              
            except:
                return False
            else:
                return True
                
    def refresh_window(self):
        self._window.refresh_all()
        
    def setup_context_help(self, item, window):
        item.Bind(wx.EVT_HELP, self.on_context_help)
        
    def on_context_help(self, event = None):
        self._window.show_help(
                      object=getattr(self._window.object, self.attribute, None), 
                      attribute = self.attribute)
        
    def hide(self):
        self.control.Hide()
        self.label.Hide()
        
    def show(self, doShow=True):
        self.control.Show(doShow)
        self.label.Show(doShow)
        
    def changed_size(self):
        """Notify the window that this attribute gui has changed size"""
        self._window.resize_puglist()
        
    def match_label_size(self):
        """Match the label height to the control height"""
        self.control.SetMinSize((-1,self.label.Size[1]))
        self.changed_size()
        
    def match_control_size(self):
        """Match the control height to the label height"""
        self.label.SetMinSize((-1,self.control.Size[1]))
        self.changed_size()
        