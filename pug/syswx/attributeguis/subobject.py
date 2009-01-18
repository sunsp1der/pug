"""SubObject agui"""

import weakref 

import wx

from pug.syswx.wxconstants import *
from pug.syswx.attributeguis import Base
from pug.syswx.pugbutton import PugButton
from pug.syswx.agui_label_sizer import AguiLabelSizer
from pug.syswx.agui_text_ctrl import AguiTextCtrl

class SubObject (Base):
    """An attribute gui for editing attributes of an object

SubObject(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugWindow. 
kwargs:
    sub_attributes: a list of the object's attributes to be shown. For example,
                    a point object might have ['x', 'y']
    no_button: normally this agui has a button to open a pugview for the object.
                    If this is true, there will be no button. Default: False
For other kwargs arguments, see the Base attribute GUI

Contains one row for each attribute listed in kwarg: 'sub_attributes'. Each row 
has a simple text entry for the sub_attribute. This has the effect of creating a
text edit gui for each sub_attribute.
    
This control is generally meant to be used for object instances, but could be 
used for any object. It is especially useful for things like vectors that are
simple objects that contain a few values in them (i.e. X and Y)
"""
    def __init__(self, attribute, window, aguidata={},**kwargs):
        #attributes
        self.kwargs = kwargs
        object = getattr(window.object,attribute)
        labelText = aguidata.get('label', 
                                 ''.join([PUGFRAME_ATTRIBUTE_PREFIX,attribute]))
        self.subControlList = []
        sub_attributes = aguidata.get('sub_attributes',[])
        if not sub_attributes:
            aguidata['sub_attributes'] = []
            kwargs['aguidata'] = aguidata
            kwargs['control_widget'] = None
            kwargs['label_widget'] = None
            Base.__init__(self, attribute, window, **kwargs)
                         
        SPACING = 4 # for button
        
        # control
        control = wx.Panel(window.get_control_window())
        controlSizer = wx.BoxSizer(orient=wx.VERTICAL)
        control.SetSizer(controlSizer)

        #label
        label = wx.Panel(window.get_label_window(), 
                         size=(1,WX_STANDARD_HEIGHT))
        labelSizer = wx.FlexGridSizer(1, 2, 0, 0)
        labelSizer.AddGrowableCol(0)
        label.SetSizer(labelSizer)
        
        subnum = 0
        subcount = len(sub_attributes)
        for sub in sub_attributes:
            subnum += 1
            controlText = AguiTextCtrl( control)
            controlText.SetMinSize((-1, WX_STANDARD_HEIGHT))
            controlText.Bind(wx.EVT_TEXT_ENTER, self.apply)
            controlText.Bind(wx.EVT_KILL_FOCUS, self.apply)
            controlHSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
            controlHSizer.Add(controlText,1)
            controlSizer.AddSizer(controlHSizer, flag = wx.EXPAND)               
            self.subControlList += [(sub,controlText)]
            rightLabel = AguiLabelSizer(label, sub, subnum == subcount, 
                                       flag=wx.ALIGN_RIGHT)
            rightLabel.SetMinSize((-1,controlText.MinSize[1]+1))
            if subnum == 1:
                if aguidata.get('no_button', False):
                    button_spacing = 0
                else:
                    # show view button in top row of control
                    newViewButton = PugButton(control, object, True, attribute, 
                                              window,
                                              targetObjectFn=self.get_object)
                    self.newViewButton = newViewButton      
                    button_spacing = SPACING + newViewButton.Size[0]
                    controlHSizer.AddSpacer((SPACING,SPACING))
                    controlHSizer.Add(newViewButton)
                    # show main label in top row of label
                leftLabel = AguiLabelSizer( label, labelText, subcount == 1)
                label.textCtrl = leftLabel.textCtrl # tooltip target
                    
            else:
                if subnum == subcount and button_spacing:
                    #add line at far right for bottom subattribute
                    underline = AguiLabelSizer( control, '')
                    underline.SetMinSize((button_spacing, -1))
                    controlHSizer.AddSizer(underline,0, flag = wx.EXPAND)
                else:
                    controlHSizer.AddSpacer((button_spacing, SPACING))
                # empty left area for rows 2 and on
                leftLabel = AguiLabelSizer( label, '', subnum == subcount)    
            leftLabel.SetMinSize((-1,controlText.MinSize[1]+1))
            labelSizer.AddSizer(leftLabel, flag = wx.EXPAND)
            labelSizer.AddSizer(rightLabel, flag = wx.EXPAND)

        control.SetSize(controlSizer.MinSize)
        control.SetMinSize((-1,controlSizer.MinSize[1]))
        label.SetMinSize(control.MinSize)
        kwargs['aguidata'] = aguidata
        kwargs['control_widget'] = control
        kwargs['label_widget'] = label
        Base.__init__(self, attribute, window, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        sub_attributes = aguidata.get('sub_attributes',[])
        old_attributes = self._aguidata['sub_attributes']
        if sub_attributes != old_attributes:
            self.__init__(self, attribute, window, aguidata)
            return
        else:
            Base.setup( self, attribute, window, aguidata)
            
    objRef = None    
    def get_object(self):
        if self.objRef:
            return self.objRef()
        else:
            object = getattr(self._window.object, self.attribute)
            self.objRef = weakref.ref(object)
            return object        

    def get_control_value(self):
        """get_control_value -> (val1, val2...)"""
        val = []
        for attr, control in self.subControlList:
            val += [control.GetValue()]
        return tuple(val)
        
    def set_control_value(self, val):
        """set_control_value(val)... val=(val1, val2...)"""
        i=0
        for value in val:            
            self.subControlList[i][1].SetValue(value)
            i+=1
        return
    
    def get_attribute_value(self, event=None):
        object = getattr(self._window.object, self.attribute)
        val = []
        for attr, control in self.subControlList:
            val += [getattr(object,attr)]
        return tuple(val)
            
    def set_attribute_value(self):
        object = getattr(self._window.object, self.attribute)
        val = self.get_control_value()
        i=0
        try:
            for attr,control in self.subControlList:
                setattr(object,attr,val[i])
                i+=1
        except:
            return False
        else:
            return True


        