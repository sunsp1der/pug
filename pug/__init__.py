"""Python Universal GUI"""

#Create a GUI for Python objects automatically

# code storage
from pug.code_storage import CodeStorageExporter, code_export

# pugviews
from pug.pugview_manager import add_pugview, set_default_pugview

# projects
from pug.ProjectInterface import ProjectInterface

# objects
from pug.component.ComponentObject import ComponentObject
import all_components
from pug.gname import GnamedObject,  get_gnamed_object
from pug.BaseObject import BaseObject
from pug.CallbackObject import CallbackObject

# windowing system specific...
from pug.syswx.app import pugApp as App
from pug.syswx.pugframe import pug_frame as frame
from pug.syswx.attributeguis import *

