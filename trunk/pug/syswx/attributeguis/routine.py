from inspect import getargspec, getdoc, ismethod

import wx
import wx.lib.buttons as buttons

from pug.constants import *
from pug.util import get_type_name
from pug.syswx.util import show_exception_dialog
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class Routine (Base):
    """An attribute gui that allows user to call a routine object
    
When runButton is pressed, if the routine takes arguments (besides self) when 
called, open a pugFnFrame. If not, just execute.
If the routine returns a value, the Routine agui pops up a dialog showing the 
return value.    
This is meant for methods, but could be used on any callable object
"""
    def __init__(self, attribute, window, aguidata, **kwargs):
        """__init__(self, attribute, window, aguidata, **kwargs)
        
special aguidata entries:
    'routine': the callable object that will be used. This is as an
        alternative to the attribute argument.
    'use_defaults': execute routine using all default args if possible
    'no_return_popup': if this is true, don't show a return value popup
See Base attribute gui for other argument info
"""
        control = wx.Panel(window, 
                           size = (1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        #widgets
        runButton = buttons.ThemedGenBitmapButton(control,  
                                                  size=WX_BUTTON_SIZE)
        
        infoText = wx.StaticText(control)
        infoText.SetMinSize((-1,infoText.Size[1]))
        line = wx.StaticLine(control, style = 0) 
        self.runButton = runButton
        self.infoText = infoText

        # sizers
        textSizer = wx.BoxSizer(orient=wx.VERTICAL)
        textSizer.AddSpacer((1,WX_TEXTEDIT_LABEL_YOFFSET))
        textSizer.Add(infoText, 1)
        textSizer.Add(line, flag = wx.EXPAND | wx.BOTTOM)
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        control.SetSizer(controlSizer)
        controlSizer.Add(runButton)
        controlSizer.AddSpacer((3,3))
        controlSizer.Add(textSizer,1,wx.EXPAND)
        control.sizer = controlSizer
        control.textSizer = textSizer
        
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
        from pug.syswx.pugframe import pug_frame
        self.pug_frame = pug_frame
        
    def setup(self, attribute, window, aguidata):
        use_defaults = aguidata.get('use_defaults', False)

        # check if the callable is provided or if it's a true attribute
        if aguidata.get('routine', False):
            value = aguidata['routine']
            self.routine = value
            if not aguidata.get('label', None):
                if attribute:
                    aguidata['label'] = attribute
                else:
                    aguidata['label'] = self.routine.__name__
            attribute = ''
        else:
            value = getattr(window.object,attribute, None)
        isMethod = bool(ismethod(value) and value.im_self)
        doc = None
        if aguidata.has_key('doc'):
            doc = aguidata['doc']
        else:
            doc = getdoc(value)
            if doc:
                aguidata['doc'] = doc

        # analyze the routine's arguments 
        if callable(value):
            self.takesargs = False
            self.needsargs = False
            self.notpython = False
            try:
                argspec = getargspec(value)
            except:
                self.notpython = True
                arguments = "?args unknown?"
            else:
                arglist = []
                if isMethod:
                    argspec[0].pop(0)
                if argspec[0]:
                    self.takesargs = True
                    mainargs = argspec[0][:]
                    if argspec[3]:
                        argcount = len(argspec[0])
                        if argcount < len(argspec[3]):
                            self.needsargs = True
                        for idx in range(argcount):
                            kwidx = idx - (argcount - len(argspec[3])) 
                            if kwidx >= 0:
                                mainargs[idx] = ''.join([argspec[0][idx],
                                                '=',repr(argspec[3][kwidx])])
                    arglist += mainargs
                if argspec[1]:
                    arglist += [''.join([ '*',argspec[1]])]
                    self.takesargs = True
                if argspec[2]:
                    arglist += [''.join([ '**',argspec[2]])]
                    self.takesargs = True
                arguments = ', '.join(arglist)
                arguments = ''.join(["(",arguments,")"])
        else:
            arguments = "?Not Callable?"
        self.arguments = arguments
        
        if (self.takesargs or self.notpython) and \
                not(use_defaults and not self.needsargs):
            bmp = wx.ART_HELP_SIDE_PANEL
            if doc:
                tooltip = doc
            else:
                tooltip = "Enter arguments"       
            fn = self.openExecuteWindow
        else:
            bmp = wx.ART_GO_FORWARD
            if doc:
                tooltip = doc
            else:
                tooltip = "Execute"
            fn = self.execute
            arguments = '()'
        buttonSize=WX_BUTTON_BMP_SIZE
        run_bmp = wx.ArtProvider.GetBitmap(bmp, 
                                        wx.ART_TOOLBAR, buttonSize)        
        self.runButton.SetBitmapLabel(run_bmp)
        self.runButton.SetToolTipString(tooltip)
        self.control.Unbind(wx.EVT_BUTTON, self.runButton)
        self.control.Bind(wx.EVT_BUTTON, fn, self.runButton)  
        self.infoText.SetLabel( arguments)   
        Base.setup(self, attribute, window, aguidata) 
        
    def get_routine(self):
        routine = getattr(self, 'routine', False)
        if routine:
            return routine
        else:
            return self.get_attribute_value()
            
        
    def execute(self, event = None):
        routine = self.get_routine()
        if callable(routine):
            try:
                wx.BeginBusyCursor()
                retValue = routine.__call__()
            except:
                wx.EndBusyCursor()                
                show_exception_dialog( self.control)
            else:
                wx.EndBusyCursor()                
                try:
                    self.display_retvalue( retValue)
                    self.refresh_window()                
                except:
                    # anything could have happened, like deleting the object etc.
                    pass
                
    def parseargs(self, *args, **kwargs):
        return (args, kwargs)
        
    def openExecuteWindow(self, event = None):
        routine = self.get_routine()
        doc = getdoc(routine)
        if (doc):
            text = doc
        else:
            text = ''.join([self.attribute,self.arguments])
        dlg = wx.TextEntryDialog(self.control, text,
                ''.join(['Enter Arguments for ',routine.__name__]))

        if dlg.ShowModal() == wx.ID_OK:
            attribute = self.attribute
            realself = self
            self = self.window.object
            exec(''.join(['(args, kwargs) = realself.parseargs(',
                               dlg.GetValue(),')']))
            self = realself
            retValue = None
            try:
                wx.BeginBusyCursor()
                retValue = routine.__call__(*args, **kwargs)
            except:
                wx.EndBusyCursor()                
                show_exception_dialog( self.control)
                self.openExecuteWindow()
            else:
                wx.EndBusyCursor()
                self.display_retvalue( retValue)
                self.refresh_window()
        dlg.Destroy()

    def display_retvalue(self, retValue):
        do_retvalue = not self.aguidata.get('no_return_popup', False)
        if not do_retvalue:
            return
        if retValue is not None:
            if type(retValue) in BASIC_TYPES:
                retDlg = wx.MessageDialog(self.control,
                                  ''.join([self.attribute,' returned:\n', 
                                       str(retValue)]),
                                   'Return Value', wx.OK)
                retDlg.ShowModal()
            else:
                retDlg = wx.MessageDialog(self.control,
                                  ''.join([self.attribute,' returned:\n', 
                                       str(retValue),
                                   '\n\nUse pug to examine returned value?']),
                                   'Return Value', wx.YES_NO | wx.NO_DEFAULT)
                showframe = None
                if retDlg.ShowModal() == wx.ID_YES:
                    showframe = self.pug_frame(obj=retValue, 
                             objectpath=get_type_name(retValue), 
                             parent=self.window)
            try:
                retDlg.Destroy()
                if showframe:
                    showframe.Raise()
            except:
                pass
        
        