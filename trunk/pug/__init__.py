"""Python Universal GUI"""

#Create a GUI for Python objects automatically

# Uncomment for ocempgui system
# from PUG.SysOcempGUI.PUGRenderer import getRenderer
# from PUG.SysOcempGUI.PUGWindow import PUGWindow

from pug.util import pugSave, pugLoad
from pug.code_storage import CodeStorageExporter, code_export
from pug.templatemanager import add_template, set_default_template
from pug.gname import GnamedObject,  get_gnamed_object
from pug.ProjectInterface import ProjectInterface
from pug.component.ComponentObject import ComponentObject
from pug.BaseObject import BaseObject

# windowing system specific...
from pug.syswx.app import pugApp as App
from pug.syswx.pugframe import pug_frame as frame
from pug.syswx.attributeguis import *