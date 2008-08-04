"""Attribute gui (AGUI) library

Attribute guis are objects that contain information for manipulating objects
that are being viewed in a pug window. They are displayed in a list in the main
frame of the window.

Attribute guis contain the following:
fields:
    label: to display a label for the control
    control: a gui control for viewing/changing an attribute 
methods:
    set_control_value: sets the control to display a value
    get_control_value: gets the control's displayed value
    apply: apply the control's value to the attribute
    refresh: apply the attribute's value to the control
"""

from pug.templatemanager import get_agui_default_dict
from pug.syswx.attributeguis.base import Base
from pug.syswx.attributeguis.generic import Generic
from pug.syswx.attributeguis.object_buttons import ObjectButtons
from pug.syswx.attributeguis.routine import Routine
from pug.syswx.attributeguis.label import Label
from pug.syswx.attributeguis.checkbox import Checkbox
from pug.syswx.attributeguis.subobject import SubObject
from pug.syswx.attributeguis.components import Components
from pug.syswx.attributeguis.dropdown import Dropdown
from pug.syswx.attributeguis.image_browser import ImageBrowser

# default attribute gui types
_AGUI_DEFAULT_DICT = {
                      #families
                          'ObjectButtons':[ObjectButtons],
                          'Routine':[Routine],
                          'Default':[Generic],
                      #types
                          bool:[Checkbox]
                     }

get_agui_default_dict().update(_AGUI_DEFAULT_DICT)