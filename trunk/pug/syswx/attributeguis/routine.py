from inspect import getargspec, getdoc
from sys import exc_info
import weakref

import wx

from pug.constants import *
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
        control = wx.Panel(window.get_control_window(), 
                           size = (1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        use_defaults = aguidata.get('use_defaults', False)

        # check if the callable is provided or if it's a true attribute
        if aguidata.get('routine', False):
            value = aguidata['routine']
            if not aguidata.get('label', None):
                if attribute:
                    aguidata['label'] = attribute
                else:
                    aguidata['label'] = value.__name__
            attribute = ''
        else:
            value = getattr(window.object,attribute, None)

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
                if argspec[0]:
                    if len(argspec[0])>1:
                        self.takesargs = True
                    if argspec[3]:
                        if len(argspec[0]) < len(argspec[3]) + 1:
                            self.needsargs = True
                    arglist += argspec[0]
                if argspec[1]:
                    arglist += [''.join([ '*',argspec[1]])]
                    self.takesargs = True
                if argspec[2]:
                    arglist += [''.join([ '**',argspec[2]])]
                    self.takesargs = True
                if arglist[0] == "self":
                    arglist.pop(0)
                arguments = ', '.join(arglist)
                arguments = ''.join(["(",arguments,")"])
        else:
            arguments = "?Not Callable?"
        self.arguments = arguments
        
        #widgets
        buttonSize=WX_BUTTON_BMP_SIZE
        if (self.takesargs or self.notpython) and \
                not(use_defaults and not self.needsargs):
            bmp = wx.ART_HELP_SIDE_PANEL
            tooltip = "Open execute window"       
            fn = self.openExecuteWindow
        else:
            bmp = wx.ART_GO_FORWARD
            tooltip = "Execute"
            fn = self.execute
            arguments = '()'
        run_bmp = wx.ArtProvider.GetBitmap(bmp, 
                                        wx.ART_TOOLBAR, buttonSize)        
        runButton = wx.BitmapButton(control, bitmap = run_bmp,
                            size = WX_BUTTON_SIZE)
        runButton.SetToolTipString(tooltip)
        control.Bind(wx.EVT_BUTTON, fn, runButton)        
        infoText = wx.StaticText(control, label = arguments)
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
        
    def execute(self, event = None):
        value = self.get_attribute_value()
        if callable(value):
            try:
                retValue = value.__call__()
            except:
                self.exception_dialog(exc_info())
            else:
                try:
                    self.display_retvalue( retValue)
                    self.refresh_window()                
                except:
                    # anything could have happened, like deleting the object etc.
                    pass

    def exception_dialog(self, info):
        err = wx.MessageDialog(self.control, str(info[1]), info[0].__name__,
                         wx.ICON_ERROR | wx.OK
                         )
        err.ShowModal()
        err.Destroy()
                
    def openExecuteWindow(self, event = None):
        value = self.get_attribute_value()
        doc = getdoc(value)
        if (doc):
            text = doc
        else:
            text = ''.join([self.attribute,self.arguments])
        dlg = wx.TextEntryDialog(self.control, text,
                ''.join(['Enter Arguments for ',self.attribute]))

        if dlg.ShowModal() == wx.ID_OK:
            attribute = self.attribute
            actualSelf = self
            self = self._window.object
            retValue = None
            command = ''.join(['retValue = self.',attribute,'(',
                               dlg.GetValue(),')'])
            try:
                exec(command)
            except:
                self = actualSelf
                self.exception_dialog(exc_info())
                self.openExecuteWindow()
            else:
                self = actualSelf
                self.display_retvalue( retValue)
                self.refresh_window()
        dlg.Destroy()

    def display_retvalue(self, retValue):
        do_retvalue = self._aguidata.get('no_return_popup', True)
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
                    self.pug_frame(obj=retValue, 
                             objectpath=retValue.__class__.__name__, 
                             parent=self._window)
            try:
                retDlg.Destroy()
                if showframe:
                    showframe.Raise()
            except:
                pass
        
        