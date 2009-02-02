"""Vector reference attribute gui AND pugview"""

import wx

from pug import add_pugview
from pug.pugview_manager import get_agui_default_dict
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis import Base, Label, SubObject
from pug.syswx.pugbutton import PugButton
from pug.syswx.agui_label_sizer import AguiLabelSizer

from Opioid2D.public.Vector import VectorReference as _opioidVectorReference
from Opioid2D.public.Vector import Vector

# attribute gui
# Not used any more... but might be worth looking at as an example of
# horizontally laid out sub-attributes
class VectorReference (Base):
    """An attribute gui for viewing Opioid2D VectorReferences

VectorReference(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame. 
For kwargs arguments, see the Base attribute GUI

Contains text showing attribute's value and two buttons... 
    viewButton: changes the parent window to display this object
    newViewButton: opens a new pug window to display objet
    
This control is generally meant to be used for instances, but could be used for
any object.
"""
    def __init__(self, attribute, window, aguidata, **kwargs):
        #widgets
        control = wx.Panel(window, size = (1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        self.object = getattr(window.object,attribute)
        #x
        xTextSizer = AguiLabelSizer(control, 'X:')
        xText = wx.TextCtrl( control, -1, 
                              size=wx.Size(30, WX_STANDARD_HEIGHT), 
                              style=wx.TAB_TRAVERSAL | wx.TE_PROCESS_ENTER)
        control.SetMinSize(wx.Size(0, WX_STANDARD_HEIGHT))
        control.Bind(wx.EVT_TEXT_ENTER, self.apply)
        #y
        yTextSizer = AguiLabelSizer(control, ' Y:')
        yText = wx.TextCtrl( control, -1, 
                              size=wx.Size(30, WX_STANDARD_HEIGHT), 
                              style=wx.TAB_TRAVERSAL | wx.TE_PROCESS_ENTER)
        control.SetMinSize(wx.Size(0, WX_STANDARD_HEIGHT))
        control.Bind(wx.EVT_TEXT_ENTER, self.apply)
        #button
        newViewButton = PugButton(control, self.object,
                               True, attribute, window)
        self.xText = xText
        self.yText = yText
        self.xTextSizer = xTextSizer
        self.yTextSizer = yTextSizer
        self.newViewButton = newViewButton 

        # sizers
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        control.SetSizer(controlSizer)
        controlSizer.AddSizer(xTextSizer,flag=wx.EXPAND)
        controlSizer.Add(xText,1)
        controlSizer.AddSizer(yTextSizer,flag=wx.EXPAND)
        controlSizer.Add(yText,1)
        controlSizer.AddSpacer((5,5))        
        controlSizer.Add(newViewButton)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def get_control_value(self):
        """get_control_value -> (X,Y)"""
        try:            
            val = eval(''.join([
                    '(',self.xText.GetValue(),',',self.yText.GetValue(),')']))
        except:
            return None
        return val
        
    def set_control_value(self, val):
        """set_control_value(val)... val=(X,Y)"""
        self.xText.SetValue(str(val[0]))
        self.yText.SetValue(str(val[1]))
        return
    
    def get_attribute_value(self, event=None):
        val = (self.object.x, self.object.y)
        return val
            
    def set_attribute_value(self):
        val = self.get_control_value()
        try:
            self.object.x = val[0]
            self.object.y = val[1]
        except:
            return False
        else:
            return True

#make the above the default attribute gui for VectorReference
get_agui_default_dict().update({_opioidVectorReference:
                                [SubObject,{'sub_attributes':['x','y'],
                                            'no_button':True}]
                                })
get_agui_default_dict().update({Vector:
                                [SubObject,{'sub_attributes':['x','y'],
                                            'no_button':True}]
                                })
        
#pug pugview
_vectorReferencePugview = {
        'name':'Basic',
        'force_persist':True,
        'attributes':
        [
            ['', Label, {'label':'Vector','font_size':10}],
            ['',Label, {'label':' Co-ordinates'}],
            ['x'],
            ['y'],
            ['',Label, {'label':' Radial'}],
            ['direction'],
            ['length']
        ]
}
add_pugview(_opioidVectorReference, _vectorReferencePugview, True) 
add_pugview(Vector, _vectorReferencePugview, True) 


        