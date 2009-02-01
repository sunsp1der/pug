"""Attribute gui (AGUI) library

Attribute guis are the building blocks of PugWindows. The different aguis are
different ways of displaying and editing data. 
"""

from pug.pugview_manager import get_agui_default_dict
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
from pug.syswx.attributeguis.play_buttons import PlayButtons
from pug.syswx.attributeguis.gname_dropdown import GnameDropdown
from pug.syswx.attributeguis.listedit import ListEdit
 
# default attribute gui types
from pug.component.ComponentObject import ComponentSet
_AGUI_DEFAULT_DICT = {
                      #families
                          'Objects':[ObjectButtons],
                          'Routine':[Routine],
                          'Default':[Generic],
                      #types
                          bool:[Checkbox],
                          ComponentSet:[Components]
                     }

get_agui_default_dict().update(_AGUI_DEFAULT_DICT)

# load other gui default stuff
from pug.component import pugview # component fanciness