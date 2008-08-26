"""Attribute gui (AGUI) library

Attribute guis are the building blocks of PugWindows. The different aguis are
different ways of displaying and editing data. 
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
                          'Objects':[ObjectButtons],
                          'Routine':[Routine],
                          'Default':[Generic],
                      #types
                          bool:[Checkbox]
                     }

get_agui_default_dict().update(_AGUI_DEFAULT_DICT)