import time

from Opioid2D import Scene, Sprite
from Opioid2D.public.Node import Node

import pug
from pug.util import CallbackWeakKeyDictionary
from pug.code_storage.constants import _INDENT
from pug.code_storage import add_subclass_skip_attributes

from pug_opioid import PugSprite
from pug_opioid.wx_agui import SceneNodes
from pug_opioid.util import get_available_objects

class PugScene( Scene, pug.BaseObject):
    """PugScene - Opioid2d Scene with features for use with pug"""
    _pugTemplateClass = 'PugScene'
    
    # node info storage
    def get_nodes(self):
        if not hasattr(self,'_nodes'):
            self._nodes = CallbackWeakKeyDictionary()
        return self._nodes
    nodes = property (get_nodes,doc="dictionary of Scene nodes:layers")
    def update_node(self, node):
        if node.deleted:
            if self.nodes.has_key(node):
                self.nodes.__delitem__(node)
            return
        try:
            gname = node.gname
        except:
            gname = ''
        try:
            layer = node.layer.name
        except:
            layer = ''
        self.nodes[node] = (gname, layer)
        
    addObjectClass = PugSprite
    def add_object(self, nodeclass=None):
        """add_object( nodeclass=None)
        
Add an object to the scene
"""
        if nodeclass is None:
            objectclass = self.addObjectClass
        if not issubclass(objectclass, Node):
            raise TypeError("add_object(): arg 1 must be a subclass of Node")
        node = objectclass()               
        
    # code storage customization
    def _create_object_code(self, storageDict, indentLevel, exporter):
        storage_name = storageDict['storage_name']
        if storage_name == 'PugScene' or \
                storage_name == 'Scene':
            raise ValueError(''.join(["Can't over-write ",
                                      storage_name," base class."]))
        # start with basic export
        base_code = exporter.create_object_code(self, storageDict, indentLevel, 
                                                True)
        baseIndent = _INDENT * indentLevel       
        custom_code_list = []
        # custom code
#        # groups
#        if self._groups:
#            custom_code_list += [baseIndent, _INDENT, 'groups = ', 
#                                 str(self._groups.keys()),
#                                 '\n']
        if storageDict['as_class']:
            # comment
            custom_code_list += [baseIndent, _INDENT, '# Sprites etc.\n']
            
            # enter function
            custom_code_list += [baseIndent, _INDENT, 'def enter(self):\n']
            nodes = self.nodes.keys()
            if nodes:
                for node in nodes:
                    nodeStorageDict = exporter.get_custom_storageDict(node)
                    nodeStorageDict['as_class'] = False # export as object
                    node_code = exporter.create_object_code(node, 
                                                            nodeStorageDict, 
                                                            indentLevel + 2,
                                                            False)                    
                    custom_code_list+=[node_code,'\n']
                    # give Opioid some time to catch up
                    starttime = time.time()
                    while time.time()-starttime < 0.05:
                        time.sleep(0.01)
            else:
                custom_code_list+=[baseIndent, _INDENT * 2, 'pass','\n']
                        
        code = ''.join([base_code] + custom_code_list)
        return code
    _codeStorageDict = {
            'custom_export_func': _create_object_code,
            'as_class':True,
            'skip_attributes': ['_nodes','_groups']
             }   
    add_subclass_skip_attributes(_codeStorageDict, pug.BaseObject)
    
# pug template stuff

def _object_list_generator():
    """_object_list_generator()-> list of objects + 'New'
    
Return a list of node classes available in the objects folder. Append to that
list a tuple ("Sprite", PugSprite) for use in the add object dropdown"""
    list = get_available_objects()
    list.insert(0,("New Sprite", PugSprite))
    return list    
            
def _reload_object_list(self):
    """Reload all saved object classes from disk"""
    try:
        scene = Opioid2D.Director.scene
    except:
        return
    get_available_objects( True)
    addName = scene.addObjectClass.__name__
    for object in objectlist:
        if object.__name__ == addName:
            scene.addObjectClass = object
                        
_sceneTemplate = {
    'name':'Basic',
    'attributes':
    [
        ['', pug.Label, {'label':'Scene','font_size':10}],
        ['gname'],
        ['layers', None, {'read_only':True}],
        ['', pug.Label, {'label':' Functions'}],
        ['add_layer'],
        ['delete_layer'],
        ['', pug.Label, {'label':' Add Object'}],
        ['addObjectClass', pug.Dropdown, 
             {'list_generator':_object_list_generator,
              'label':'   Object to add',
              'tooltip':'Select an object type for the add button below'}],
        ['add_object', None, {'tooltip':\
              'Add an object to the scene.\nSelect object type above.',
                              'use_defaults':True,
                              'label':'   Add Object'}],
        ['', pug.Routine, {'label':'   Reload Objects', 
                    'routine':_reload_object_list}],
        ['', pug.Label, {'label':' Scene Nodes'}],
        ['nodes', SceneNodes, {'growable':True}],
    ]
}
pug.add_template('PugScene', _sceneTemplate, True)
