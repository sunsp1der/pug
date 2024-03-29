"""Base class for attribute guis"""
import time
from inspect import isclass
from functools import partial

import wx

from pug.util import get_type_name, get_type
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
        'doc': the tooltip that will pop up on the label
        'background_color': for label_widget and control_widget call 
            'SetBackgroundColor' with this value
        'growable': if true, this allows the control to grow vertically
        'agui_info_dict': a dict that will be filled with:
                            'agui':the actual agui created
        'refresh_all': When attribute changes, refresh pug view. Default: True.
        'wait_for_set': Wait for confirmation when setting attribute. 
                        Default:True
        'undo': Register changes in attribute with undo/redo history.
                    Default: True
        
control_widget: the widget used for input, usually defined by derived classes. 
label_widget: widget used for label. For compatibility, this control should have
    a textCtrl member that contains the main piece of text.

Attribute guis should almost always be derived from Base. Base.label is the
label displayed on the left of a pugFrame. Base.control is the control displayed
on the right of a pugFrame.

The main functions that attribute guis are meant to over-ride are:
set_control_value(self, val): make Base.control display val
get_control_value(self): return the value shown in Base.control
setup(self, attribute, window, aguidata): reset all values in the agui but
    don't recreate any wx controls. This is important when a cached agui is
    re-used.

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
    applying = False
    def __init__(self, attribute, window, aguidata = {}, control_widget = None, 
                 label_widget = None, **kwargs):
        self.aguidata = aguidata
        self.window = window
        self.attribute = attribute
        # control
        if control_widget:
            self.control = control_widget
        else:
            # no control provided, so just make an empty panel
            self.control = wx.Panel(window, size = (1,WX_STANDARD_HEIGHT))
            
        # label    
        if label_widget:
            self.label = label_widget
        else:
            #panel
            label = wx.Panel(window, style=0,
                             size=(0, self.control.Size[1]))
            #label
            labelSizer = AguiLabelSizer(label)
            label.SetSizer(labelSizer)
            label.textCtrl = labelSizer.textCtrl
            self.label = label
                        
        self.setup( attribute, window, aguidata)
                
    def setup(self, attribute, window, aguidata):
        """setup(attribute, window, aguidata)
 
Setup agui. Called on creation and when a cached agui is re-used on another 
object. Allows an agui to change object, window, or aguidata without recreating
all controls.
"""
        if attribute is not None:            
            self.attribute = attribute  
        if aguidata is not None:         
            self.aguidata = aguidata
        if window is not None:
            self.window = window
        if self.control.GetParent() != self.window:
            self.control.Reparent(self.window)
            if self.control.IsFrozen():
                self.control.Thaw()
            self.control.Show()
        if self.label.GetParent() != self.window:
            self.label.Reparent(self.window)
            if self.label.IsFrozen():
                self.label.Thaw()
            self.label.Show()
        aguidata.setdefault('read_only',False)
        aguidata.setdefault('refresh_all', True)
        aguidata.setdefault('wait_for_set', True)
        aguidata.setdefault('undo', True)
        #label
        if hasattr(self.label, 'textCtrl'):
            labelText = aguidata.get('label', 
                                 ''.join([PUGFRAME_ATTRIBUTE_PREFIX,attribute]))
            self.label.textCtrl.SetLabel( labelText)
        #tooltip
        self.tooltip = None
        if aguidata.has_key('doc'):
            self.tooltip = aguidata['doc']
        else:
            try: # check if this is a property
                if isclass(window.object):
                    cls = window.object
                else:
                    cls = get_type(window.object)
                prop = getattr(cls, attribute, None)
                if type(prop) == property:
                    self.tooltip = prop.__doc__
            except:
                pass
        if self.tooltip:
            self.set_label_tooltip(self.tooltip) 
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
        
        #info
        if aguidata.has_key('agui_info_dict'):
            aguidata['agui_info_dict']['agui'] = self        
            
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
        if get_type(value) not in BASIC_TYPES:
            doc = getattr(value,'__doc__','')
        elif value is not None:
            try:
                doc = get_type_name(value)
            except:
                pass
        try:
            self.set_label_tooltip(doc)            
        except:
            if hasattr(self.label, 'text'):
                if self.label.GetToolTip():
                    self.set_label_tooltip(' ')            
        
    def set_label_tooltip(self, tip, control=None):
        if control == None:
            control = self.label
        control.SetToolTipString( tip)
        for child in control.GetChildren():
            self.set_label_tooltip( tip, child)
        
    def get_attribute_value(self):
        return getattr(self.window.object, self.attribute, None)
 
    def apply(self, event = None):
        """Apply change to object
        
When auto apply is off, skip apply events that were created by the event system        
"""
        # when auto apply is off, skip apply events that were created by the 
        # event system
        if self.applying:
            return
        self.applying = True
        if not self.window.settings['auto_apply'] and event:
            self.applying = False
            return False
        # see if we even need to do anything
        try:
            control_value = self.get_control_value()
        except:
            self.applying = False
            return False
        attribute_value = self.get_attribute_value()
        if attribute_value == control_value:
            # no need to set... effectively, our work is done successfully
            self.applying = False
            return True
        # we need to set, but make sure attribute is not readonly
        if self.aguidata['read_only']:
            # this creates a loop by changing focus automatically
            retDlg = wx.MessageDialog(self.control, 
                              ''.join([self.attribute,
                                       ' cannot be editted via gui']), 
                               'Read Only', wx.OK)
            retDlg.ShowModal() 
            retDlg.Destroy()          
            applied = False   
        else:                
            applied = self.set_attribute_value()
        if applied:
            if self.aguidata['wait_for_set']:
                starttime = time.time()
                while self.get_attribute_value() != control_value:
                    # sometimes we have to wait a bit for it to take effect
                    # if this takes more than 0.5 seconds, forget it
                    
                    # HACK check for weird float case
                    if type(control_value) == type(0.1):
                        if type(self.get_attribute_value()) == type(0.1) and \
                                str(self.get_attribute_value()) == \
                                str(control_value):
                            break            
                    time.sleep(0.01)
                    if time.time() - starttime > 0.5: 
                        applied = False
                        self.refresh()
                        break
            if self.aguidata['refresh_all']:
                self.refresh_window()        
            #self.set_control_value(self.get_control_value())          
        else:
            # bad apply... just revert
            self.refresh()  
        self.applying = False
        return applied

    def get_control_value(self):
        """get the value of the attribute - defined by derivative classes

By default, this returns the attribute value        
"""
        return getattr(self.window.object, self.attribute, None)

    def set_attribute_value(self):
        """set_attribute_value(val)->False if there was a problem, else True.
        
Try to set the aguis attribute to the value shown in the control. This is where
pug registers with its undo system. For info, see pug.history_manager.
"""
        try:
            current_value = self.get_attribute_value()
            control_value = self.get_control_value()
#            setattr(self.window.object, self.attribute, control_value)              
            do_fn = partial( setattr, 
                             self.window.object,                                         
                             self.attribute, 
                             control_value)
            undo_fn = partial( setattr,
                               self.window.object,
                               self.attribute,
                               current_value)
            do_fn()
        except:
            return False
        else:
            if self.aguidata['undo']:
                wx.GetApp().history.add(
                            "Set "+self.attribute+" of "+self.window.shortPath, 
                            undo_fn, do_fn, 
                            (self.window.object, self.attribute))
            return True
                
    def refresh_window(self):
        self.window.refresh()
        
    def setup_context_help(self, item, window):
        item.Bind(wx.EVT_HELP, self.on_context_help)
        
    def on_context_help(self, event = None):
        self.window.show_help(
                      object=getattr(self.window.object, self.attribute, None), 
                      attribute = self.attribute)
        
    def hide(self):
        self.control.Hide()
        self.label.Hide()
        
    def show(self, doShow=True):
        self.control.Show(doShow)
        self.label.Show(doShow)
        
    def changed_size(self):
        """Notify the window that this attribute gui has changed size"""
        self.window.resize_aguilist()
        
    def match_label_size(self, doWindowResize=False):
        """Match the label height to the control height"""
        self.control.SetMinSize((-1,self.label.Size[1]))
        if doWindowResize:
            self.changed_size()
        
    def match_control_size(self, doWindowResize=False):
        """Match the control height to the label height"""
        self.label.SetMinSize((-1,self.control.Size[1]))
        if doWindowResize:
            self.changed_size()
        