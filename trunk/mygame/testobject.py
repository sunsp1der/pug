import pug
from pug.syswx.attributeguis import *
from pug.component import test

#------------------------------------------------------------------------------ 
class fake( pug.BaseObject):
    """Test object"""
    def __init__(self):
        pug.BaseObject.__init__(self)
        
_fakePugview = {
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
pug.add_pugview(fake,_fakePugview,True)