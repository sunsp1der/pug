import os.path

import Opioid2D

import pug
from pug.util import CallbackWeakKeyDictionary
from pug.code_storage.constants import _INDENT
from pug.code_storage import add_subclass_skip_attributes

from pug_opioid.editor.wx_agui import SceneNodes, SceneLayers
from pug_opioid.editor.util import get_available_layers, save_object

_DEBUG = False

class PugScene( Opioid2D.Scene, pug.BaseObject):
    """PugScene - Opioid2d Scene with features for use with pug"""
    __node_num = 0
    _pug_template_class = 'PugScene'
    def __init__(self, gname=''):
        Opioid2D.Scene.__init__(self)
        pug.BaseObject.__init__(self, gname)        

    def handle_keydown(self, ev):
        if ev.key == Opioid2D.K_ESCAPE:
            if getattr(Opioid2D.Director, 'playing_in_editor', False):
                import wx
                wx.CallAfter(wx.GetApp().projectObject.stop_scene)
            else:
                Opioid2D.Director.quit()

    def start(self):
        """call after enter() and before state changes"""
        if not getattr(Opioid2D.Director, 'game_started', False):
            if getattr(Opioid2D.Director, 'start_game', False):
                for node in self.get_ordered_nodes():
                    if node.archetype:
                        node.delete()
                Opioid2D.Director.game_started = True                        
                self.all_nodes_callback( 'on_game_start')
                self.all_nodes_callback( 'on_added_to_scene', self)        
            else:
                # do nothing if we're not starting the game
                return
        self.all_nodes_callback( 'on_scene_start', self)             
    
    def stop(self):
        """Stop a level that is playing"""
        Opioid2D.Director.game_started = False  
        Opioid2D.Director.start_game = False                     
    
    def all_nodes_callback(self, callback, *args, **kwargs):
        """Send a callback to all nodes in the scene"""
        for node in self.nodes:
            self.node_callback( node, callback, *args, **kwargs)
                
    def node_callback(self, node, callback, *args, **kwargs):
        """Send a callback to a node in the scene"""
        if hasattr(node, callback):
            func = getattr(node, callback)
            func( *args, **kwargs)
        
    # node info storage
    def _get_nodes(self):
        """_get_nodes()->CallbackWeakKeyDictionary of nodes"""
        if not hasattr(self,'_nodes'):
            self._nodes = CallbackWeakKeyDictionary()
        return self._nodes

    nodes = property (_get_nodes,doc="dictionary of Scene nodes:node_num")

    def get_ordered_nodes(self):
        """get_ordered_nodes()->list of nodes sorted by layer then create-time
        
Note that due to the non-deterministic nature of Opioid zordering, the order
returned will be from top to bottom in terms of layers, but pseudo-random in
terms of nodes within the layers"""
        nodelist = []
        if self.nodes:
            # create ordered list of nodes
            layers = self.get_scene_layers()[:]
            layersort = {}
            a = 1
            for layer in layers:
                layersort[layer] = '%03d'%a
                a+=1
            ordered_nodes = {}
            myNodes = self.nodes.keys()
            for node in myNodes:
                if hasattr(node.layer,'name'):
                    nodesorter = '_'.join([layersort[node.layer_name],
                                       '%04d'%self.nodes[node]])
                else:
                    nodesorter = '_'.join(['000',
                                       '%04d'%self.nodes[node]])
                    if _DEBUG:
                        import gc
                        gc.collect()
                        print "get_ordered nolayer", str(node), node.gname
                        node._test_referrers()
#                       self.nodes.pop(node)
#                    continue
                ordered_nodes[nodesorter] = node
            nodenums = ordered_nodes.keys()
            nodenums.sort()
            nodenums.reverse()
            for num in nodenums:
                nodelist.append(ordered_nodes[num])
        return nodelist

    def pick_all(self, x, y):
        """pick_all(x,y)

Get all nodes whose rects overlap (x,y)
"""
        nodelist = self.get_ordered_nodes()
        picklist = []
        for node in nodelist:
            rect = node.rect
            if rect.collidepoint(x, y):
                picklist.append(node)  
        return picklist

    def pick(self, x, y, selectedRefSet=None):
        """pick(x, y, selectedRefSet=[])->return a node to select at x,y
        
x,y: coordinates
selectedRefSet: a list of selected objects. If possible, pick will return an 
    object at x,y that is NOT in the list.
"""
        if selectedRefSet is None:
            selectedRefSet = []
        picklist = self.pick_all(x, y)
        if not len(picklist):
            return None
        if len(picklist) == 1 or not selectedRefSet:
            return picklist[0]
        start_node = None
        selected_list = []
        for ref in selectedRefSet:
            selected_node = ref()
            selected_list.append(selected_node)
            if not start_node and selected_node in picklist:
                start_node = selected_node
        if start_node:
            start_idx = picklist.index(start_node)
            idx = start_idx + 1
            while idx != start_idx:
                if idx >= len(picklist):
                    idx = 0
                try_node = picklist[idx]
                if try_node in selected_list:
                    idx = idx + 1
                    continue
                else:
                    return try_node
        else:
            return picklist[0]

    def update_node(self, node, command=None):
        """update_node(node, command=None)
        
Update the PugScene's node tracking dict for node. Possible commands: 'Delete'
"""
        nodes = self.nodes
        if _DEBUG: print "pugscene.update_node", node, command
        if getattr(node,'deleted',False) or command == 'Delete':
            if nodes.has_key(node):
                try:
                    nodes.__delitem__(node)
                    if _DEBUG: print "   deleted"
                except:
                    if _DEBUG: print "   could not delete (already gone?)"
            else:
                if _DEBUG: print "   unable to delete"
            return            
        if not nodes.has_key(node):
            if _DEBUG: print "   added"
            if getattr(Opioid2D.Director, 'game_started', False):
                self.node_callback(node, "on_added_to_scene", self)
            node_num = self.__node_num
            self.__node_num += 1
        else:
            if  _DEBUG: print "   check"
            node_num = nodes[node]
        # node_num tracks the order of node additions
        nodes[node] = node_num # this call sets off callbacks for nodes gui
            
    def get_scene_layers(self):
        return get_available_layers()

    scene_layers = property(get_scene_layers, doc=
            'Utility property for viewing layers without __selections__ layer')
    
    # code storage customization
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if _DEBUG: print "*******************enter scene save"
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
            # enter function
            custom_code_list += [baseIndent, _INDENT, 'def enter(self):\n']
            custom_code_list += [baseIndent, _INDENT*2, '# Sprites etc.\n']
            if self.nodes:
                # create ordered list of nodes
                nodes = self.get_ordered_nodes()
                nodes.reverse() # store them from bottom-most to top-most
                for node in nodes:
                    nodeStorageDict = exporter.get_custom_storageDict(node)
                    if node.archetype:
                        # this node is a class archetype, figure out a save name
                        if node.gname:
                            savename = node.gname
                        else:
                            # no gname, so find an available filename
                            tryname = base_tryname = 'MyObjectClass'
                            savename = ''
                            suffix = 1
                            while not savename:
                                path = os.path.join('objects',
                                                    ''.join([tryname,'.py']))
                                try:
                                    file(path)
                                except:
                                    savename = tryname
                                else:
                                    suffix+=1
                                    tryname = ''.join([base_tryname, 
                                                       str(suffix)])
                            node.gname = savename
                        save_object( node, savename)
                        module = __import__('.'.join(['objects',savename]),
                                           fromlist=[savename])
                        reload(module)
                        node.__class__ = getattr(module,savename)
                        nodeStorageDict['name'] =''.join([savename,'_instance'])
                    nodeStorageDict['as_class'] = False # export as object
                    node_code = exporter.create_object_code(node, 
                                                            nodeStorageDict, 
                                                            indentLevel + 2,
                                                            False)                    
                    custom_code_list+=[node_code,'\n']
                    # hack - nasty hack
                    # give Opioid some time to catch up
#                    starttime = time.time()
#                    while time.time()-starttime < 0.5:
#                        time.sleep(0.01)
            custom_code_list += [baseIndent, _INDENT*2, '# Pug auto-start\n']
            custom_code_list += [baseIndent, _INDENT * 2, 'self.start()','\n']
        if base_code.endswith('pass\n') and custom_code_list: 
            # clean up pass case (for looks)
            base_code = base_code.splitlines()[0:-1]
            base_code.append('\n')
        else:
            base_code = [base_code]
        #add layers line
        base_code += [baseIndent, _INDENT,'layers = ', 
                      str(get_available_layers()),'\n']
        code = ''.join(base_code + custom_code_list)
        if _DEBUG: print "*******************exit scene save"
        return code
    
    _codeStorageDict = {
            'custom_export_func': _create_object_code,
            'as_class':True,
            'skip_attributes': ['_nodes','_groups','scene_layers','layers',
                                '_PugScene__node_num']
             }   
    add_subclass_skip_attributes(_codeStorageDict, pug.BaseObject)

# force derived classes to use PugScene as base class
PugScene._codeStorageDict['base_class']=PugScene
# pug template stuff
            
_sceneTemplate = {
    'name':'PugScene Editor',
    'skip_menus':['Export'],    
    'attributes':
    [
        ['Scene', pug.Label, {'font_size':10}],
        ['__class__', None, {'label':'   class', 'new_view_button':False}],        
        ['scene_layers', SceneLayers],
#        ['scene_groups', SceneGroups],
#        ['scene_layers', None, {'label':'   layers','read_only':True}],
#        ['   Save Scene', pug.Routine, {'routine':save_scene, 
#                                        'use_defaults':True}],        
#        ['   Save Scene As', pug.Routine, {
#                               'routine':save_scene_as, 
#                               'use_defaults':True,
#                               'tooltip':"Save scene to disk with new name"}],        
        [' Scene Graph', pug.Label],
        ['nodes', SceneNodes, {'growable':True}],
    ]
}
pug.add_template('PugScene', _sceneTemplate, True)
