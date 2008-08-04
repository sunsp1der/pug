import pug
from pug.syswx.attributeguis import *

#------------------------------------------------------------------------------ 
class fake( pug.BaseObject):
    """Test object"""
    def __init__(self):
        pug.BaseObject.__init__(self)
        
_fakeTemplate = {
         'name':'Basic',
         'attributes':
        [
             ['',Label,{'label':'Test'}],
             ['',Components],
             ['',Label,{'label':'Bottom'}],
             ['mygame'],
             ['interface']
         ]
        }
pug.add_template(fake,_fakeTemplate,True)