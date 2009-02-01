"""For now this is an object that is meant to keep attributes for the 
pug root (initial) frame of a pug project

methods meant for override:
   _post_init: ProjectInterface will attempt to execute this method when it is
        created. ProjectInterface._isReady will not be set until this method 
        been successfully exec'ed (onReady callback will be called). The pug 
        interface frame will only be created AFTER this method has been 
        successfully executed. This allows you to start pug with a view of 
        objects that aren't available before entering the main loop.
"""

#TODO: add a 'close all project sub-windows' function
#TODO: add a 'quit project function'
import sys
import traceback
from time import sleep
from weakref import ref

import pug
_PROFILE = False

class ProjectInterface(object):
    """Pug's starting frame"""
    _isReady = False        
    def _try_post_init(self):
        """_try_post_init-> return None, or exception string if method fails
Try to exec all the __postInitExecs
"""
        try:
            if _PROFILE:
                import profile
                profile.runctx("self._post_init()", globals(), locals(),
                               '_post_init.prof')
            else:
                self._post_init()
        except:
            return list(sys.exc_info())+[str(traceback.format_exc())]
        self._isReady = True
        return None
    
    def _post_init(self):
        """_post_init()

Derived classes can override this with any code that needs to run after the
application starts. For example, opening pug frames for app objects....
"""
        pass
    
