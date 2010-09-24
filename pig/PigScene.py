import os.path
from weakref import WeakKeyDictionary
import warnings
import sys
import traceback

from pygame.locals import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.key import get_pressed

import Opioid2D
from Opioid2D.internal.objectmgr import ObjectManager
from Opioid2D.public.Scene import SceneCallbacks

import pug
from pug.CallbackWeakKeyDictionary import CallbackWeakKeyDictionary
from pug.code_storage.constants import _INDENT
from pug.code_storage import add_subclass_storageDict_key

from pig.PauseState import PauseState
from pig.util import entered_scene
from pig.editor.agui import SceneNodes, SceneLayers
from pig.editor.util import get_available_layers, save_object, exporter_cleanup
from pig.keyboard import keys, keymods
from pig.PigDirector import PigDirector
from pig.gamedata import create_gamedata
from pig.PigMouseManager import PigMouseManager

_DEBUG = False     

class PigScene( Opioid2D.Scene, pug.BaseObject):
    """PigScene - Opioid2d Scene with features for use with pug"""
    mouse_manager = None
    __node_num = 0
    started = False
    exitted = False
    _pug_pugview_class = 'PigScene'
    layers = ['Background']
    k_info = []
    keys_pressed = None # efficiency for key register double-check
    def __init__(self, gname=''):
        if _DEBUG: print "do PigScene.__init__",self
        self._key_down_dict = {}
        self._key_up_dict = {}
        self._collision_callback_dict = WeakKeyDictionary()
            # 2D dict by sprite, then (collide-with-Group, this-sprite-Group)
        self.k_info = [self.register_key_up(keys["ESCAPE"], self.keypause),
                       self.register_key_up((keymods["CTRL"],
                                               keys["Q"]), self.keyquit)]
        Opioid2D.Scene.__init__(self)
        pug.BaseObject.__init__(self, gname)   
        if _DEBUG: print "PigScene.__init__ done", self.__class__.__name__ 
        
    def register_collision_callback( self, sprite, fn, 
                                     toGroup="colliders",
                                     fromGroup="colliders", 
                                     ignore_duplicate=False):
        """register_collision_callback(sprite, fn, toGroup, fromGroup)->Add
        
sprite: when this sprite collides with toGroup, fn will be called 
fn: the function to be called with args: (sprite, sprite-it-hit)
toGroup: sprite's group. collisions will be detected by checking fromGroup 
    sprites vs toGroup sprites. defaults to "colliders" if not specified. 
    'sprite' will automatically be added to this group.
fromGroup: when 'sprite' collides with this group, fn will be called. Defaults 
    to 'colliders' if not specified.
ignore_duplicate: if fn is already in the list of callbacks for this 
    sprite/group combination, do not add a second call
    
return value: True if the method was added, False if not (usually because it was
a duplicate and ignore_duplicate was set to True)

Designing fromGroup and toGroup efficiently will improve program 
performance. Avoid setting up situations where unnecessary collisions tests are
made.  
"""     
        sprite.join_collision_group(toGroup)
        idx1 = sprite
        idx2 = (toGroup, fromGroup)
        sprite_dict = self._collision_callback_dict.get(idx1)
        if not sprite_dict:
            self._collision_callback_dict[idx1] = {idx2:[fn]}
        else:
            callback_list = sprite_dict.get(idx2)
            if not callback_list:
                sprite_dict[idx2] = [fn]
            else:
                if ignore_duplicate and (fn in callback_list):
                    return False
                callback_list.append(fn)
        self._collision_handlers[toGroup, fromGroup] = self.collide_callbacker
        self._cObj.EnableCollisions(toGroup, fromGroup)
        return True

    def collide_callbacker( self, toSprite, fromSprite, toGroup, fromGroup,
                              check_reverse=True):
        """collision_callbacker(...)
        
args: (toSprite, fromSprite, toGroup, fromGroup, check_reverse)
toSprite: sprite that collided
fromSprite: sprite it collided with
toGroup: group that toSprite was checked as
fromGroup: group that fromSprite was checked as
check_reverse: if True, automatically checks the reverse collision. That is,
    collision_callbacker( fromSprite, toSprite, fromGroup, toGroup)

This method calls back individual sprites that have registered for collision
callbacks using register_collision_callback
"""        
        collision_dict = self._collision_callback_dict
        try:
            callback_list = collision_dict[toSprite][(toGroup, fromGroup)]
        except:
            pass
        else:
            for callback in callback_list:
                callback( toSprite, fromSprite, toGroup, fromGroup)
# WAS THIS UNNECESSARY AFTER ALL!?                
        # we only get one callback, so check if fromSprite needs a call
        # this is slow and could possibly be improved
#        if check_reverse:
#            self.collide_callbacker( fromSprite, toSprite, fromGroup, toGroup, 
#                                   False)
        
    def unregister_collision_callback(self, sprite, toGroup=None,fromGroup=None): 
        """unregister_collision_callback( sprite, toGroup, fromGroup)
        
sprite: the sprite to unregister
toGroup: If specified, only collisions as a member of this group will be
    unregistered
fromGroup: If specified, only collisions with this group will be unregistered.
"""
        sprite_dict = self._collision_callback_dict.get(sprite, {})
        if fromGroup or toGroup:
            keys = sprite_dict.keys()
            for key in keys():
                if (fromGroup is None or key[0]==fromGroup) and \
                        (toGroup is None or key[1]==toGroup):
                    sprite_dict.pop(key)
        elif sprite_dict:
            self._collision_callback_dict[sprite]={}
            pass
            
    def handle_keydown( self, ev):
        """handle_keydown( ev): ev is a pygame keydown event"""
        self.process_keylist( ev)

    def handle_keyup( self, ev):
        """handle_keydown( ev): ev is a pygame keyup event"""
        self.process_keylist( ev)
        
    def handle_mousebuttondown(self, ev):
        """handle_mousebuttondown( ev): ev is a pygame mousebuttondown event""" 
        self.process_keylist( ev)
        
    def handle_mousebuttonup(self, ev):
        """handle_mousebuttonup( ev): ev is a pygame mousebuttonup event""" 
        self.process_keylist( ev)        
        
    def process_keylist( self, ev):
        """process_keylist( ev): call registered key event callbacks

ev: a pygame key event
key_dict: the key_dict to use 
"""
        if ev.type == KEYDOWN:
            dict = self._key_down_dict
            key = ev.key
        elif ev.type == KEYUP:
            dict = self._key_up_dict
            key = ev.key
        elif ev.type == MOUSEBUTTONDOWN:
            dict = self._key_down_dict
            key = 1000 + ev.button
        elif ev.type == MOUSEBUTTONUP:
            dict = self._key_up_dict
            key = 1000 + ev.button

        mod = 0 
        if hasattr(ev,"mod") and ev.mod is not 0:
            for modval in keymods.itervalues():
                if ev.mod & modval:
                    mod += modval 
        
        fn_list = dict.get(( mod, key), [])
        for fn_info in fn_list:
            fn_info[0](*fn_info[1],**fn_info[2])

    def register_key_down(self, *args, **kwargs):
        """register_key_down(key, fn, *args, **kwargs)
    
Register a function to execute when a given key is pressed. If the key is being
pressed when this is registered, the function will be executed immediately
unless the kwarg _do_immediate is set to False.
key: can be either a KEY_ constant from pig.keyboard or a tuple in the form 
    (KEYMOD_ constant, KEY_ constant)
fn: the function to call when the keypress occurs
*args, **kwargs: arguments to fn    
"""
        # if key is already down, perform function
        if kwargs.pop('_do_immediate', True):
            try:
                pressed = get_pressed()[args[0]]
            except:
                pass
            else:
                if pressed:
                    args[1](*args[2:],**kwargs)
        return self._register_key( self._key_down_dict, *args, **kwargs)
        
    def register_key_up(self, *args, **kwargs):
        """register_key_up(key, fn, *args, **kwargs)

Like register_key_down, but when key is released"""
        return self._register_key( self._key_up_dict, *args, **kwargs)

    def unregister_key_down(self, key, fn=None, *args, **kwargs):
        """unregister_key_down(key, fn=None, *args, **kwargs)
    
Unregister a function to execute when a given key is pressed. Returns True if fn
is found. If no function is specified, unregister that key altogether and return
True.
key: can be either a KEY_ constant from pig.keyboard or a tuple in the form 
    (KEYMOD_ constant, KEY_ constant)
fn: the function to call when the keypress occurs
*args, **kwargs: arguments to fn    
"""
        self._unregister_key( self._key_down_dict, *args, **kwargs)

    def unregister_key_up(self, *args, **kwargs):
        """unregister_key_up(key, fn=None, *args, **kwargs)
        
Like register_key_down, but when key is released"""
        self._unregister_key( self._key_up_dict, *args, **kwargs)
        
    def _register_key( self, keydict, key, fn, *args, **kwargs):
        """register_key( keydict, key, fn, *args, **kwargs)->unregister tuple

key: can be either a KEY_ constant from pig.keyboard or a tuple in the form 
    (KEYMOD_ constant, KEY_ constant)
fn: the fn to be registered
*args, **kwargs: sent to fn

returns a tuple that can be sent to unregister_key to unregister the callback

Registers keys into the specified dict... avoid duplicating code for key_up,
key_down. In the future, maybe key_hold.
"""
        if key is None:
            # this facilitates components that don't use every key
            return
        else:
            try:
                keymod = key[0]
                key = key[1]
            except:
                # key must just be a keymode
                keymod = 0
        if keydict.get((keymod, key)) is None:
            keydict[(keymod, key)] = [(fn, args, kwargs)]
        else:
            keydict[(keymod, key)].append((fn, args, kwargs))
        return (keydict, (keymod, key), fn, args, kwargs)

    def unregister_key(self, info):
        """unregister_key( info)->True if key unregistered
        
info: a tuple of info returned by one of the register_key methods. 
      Contains (keydict, keymod, key, fn, args, kwargs)
"""
        if info is None:
            return
        return self._unregister_key( info[0], info[1], info[2], 
                                     *info[3], **info[4])

    def _unregister_key( self, keydict, key, fn=None, *args, **kwargs):
        """unregister_key( keydict, key, fn, *args, **kwargs)
        
Unregisters keys into the specified dict... avoid duplicating code for key_up,
key_down. In the future, maybe key_hold.
"""
        if key is None:
            # this facilitates components that don't use every key
            return
        else:
            try:
                keymod = key[0]
                key = key[1]
            except:
                # key must just be a keymode
                pass
        fn_list = keydict.get((keymod, key)) 
        if fn_list is None:
            return False
        if fn is None:
            keydict[(keymod, key)] = []
            return True
        elif (fn, args, kwargs) in fn_list:
            fn_list.remove((fn, args, kwargs))
            return True
        else:
            return False
    
    def keyquit(self):
        if getattr(Opioid2D.Director, 'viewing_in_editor', False):
            import wx
            wx = wx
            wx.CallAfter(wx.GetApp().projectObject.stop_scene)
        else:
            Opioid2D.Director.quit()
            
    def keypause(self):
        self.set_state(PauseState)
            
    def handle_quit(self, ev):
        try:
            import wx
            wx = wx
            wx.CallAfter(wx.GetApp()._evt_project_frame_close)
        except:
            Opioid2D.Director.quit()      
                
    def enter(self):
        self.mouse_manager = PigMouseManager()
        if getattr(PigDirector, 'viewing_in_editor', False) and \
                getattr(PigDirector, 'start_project', False):
            # notify scene window
            try:
                entered_scene()
            except:
                pass
        self.on_enter()
        self.start()
        
    def start(self):
        """start()

Start the scene running. Called after enter() and before state changes
"""
        if getattr(PigDirector, 'start_project', False):
            for node in self.get_ordered_nodes():
                if node.archetype:
                    node.delete()
            if not getattr(PigDirector, 'game_started', False):
                PigDirector.game_started = True
                gamedata = create_gamedata()
                gamedata.start_sceneclass = self.__class__                   
                self.on_game_start()
                self.all_nodes_callback( 'on_game_start')
            self.on_start()
            self.all_nodes_callback( 'on_added_to_scene', self)
            self.all_nodes_callback( 'on_first_display')        
        elif getattr(PigDirector, 'viewing_in_editor', False):
            # viewing in editor, not playing
            self.all_nodes_callback( 'on_added_to_editor', self)
        self.all_nodes_callback( 'on_scene_start', self)             
        self.started = True
        
    def register_node(self, node):        
#        """register(node): a new node is joining scene. Do callbacks"""
        if _DEBUG: print "PigScene.register_node:",node
        if getattr(PigDirector, 'game_started', False):
            try:
                func = getattr(node, 'on_added_to_scene')
            except:
                pass
            else:
                func(self)
            try:
                func = getattr(node,'on_first_display')
            except:
                pass
            else:
                func()
        elif getattr(PigDirector, 'editorMode', False):
            try:
                func = getattr(node, 'on_added_to_editor')
            except:
                pass
            else:
                func(self)
        self.nodes[node] = self.__node_num
        self.__node_num += 1        
        
    
    def all_nodes_callback(self, callback, *args, **kwargs):
        """Send a callback to all nodes in the scene"""
        if _DEBUG: print "PigScene.all_nodes_callback:",callback,self.nodes.data
        nodes = self.nodes.copy()
        for node in nodes:
            try:
                func = getattr(node, callback)
            except:
                pass
            else:
#                if _DEBUG: print "PigScene.node_callback",callback,node
                func( *args, **kwargs)
                        
    def on_start(self):
        """Callback hook for when scene starts playing"""
        pass

    def on_enter(self):
        pass
    
    def on_game_start(self):
        """Callback hook for when project starts with this scene"""
        pass
    
    def on_exit(self):
        """Callback hook for when scene is exitted"""
        pass
    
    def stop(self):
        """Stop a level that is playing"""
        Opioid2D.Director.game_started = False  
        Opioid2D.Director.start_project = False                     
        self.started = False
        self.exit()
        
    def exit(self):
        if _DEBUG: print "PigScene.exit"
        if not self.exitted:
            #if _DEBUG: 
            if _DEBUG: print "do PigScene.exit", self
            self.on_exit()
            self.all_nodes_callback('on_exit_scene', self)
            nodes = self.nodes.keys()
            for node in nodes:
                if _DEBUG: print "   Delete Node:",node
                try:
                    node.delete()
                except:
                    pass
            self._key_up_dict = {}
            self._key_down_dict = {}
            self._tickfunc = None
            self._realtickfunc = None
            self._callbacks = None
            self._state = None
            self._collision_callback_dict = None
            self._collision_handlers = None
            for info in self.k_info:
                try:
                    self.unregister_key( info)
                except:
                    pass
            self.k_info = []
            self.exitted = True
        else:
            pass
                               
    # node info storage
    def _get_nodes(self):
        """_get_nodes()->CallbackWeakKeyDictionary of nodes"""
        if not hasattr(self,'_nodes'):
            self._nodes = CallbackWeakKeyDictionary()
        return self._nodes

    nodes = property (_get_nodes,doc="dictionary of Scene nodes:node_num")

    def get_ordered_nodes(self, include_all=False):
        """get_ordered_nodes(include_all=False)->list of nodes 
        
Return a list of scene nodes, sorted by layer then create-time.
include_all: if True, return nodes that are not in a layer. This is a weird case
    used mainly for debugging
        
Note that due to the non-deterministic nature of Opioid z-ordering, the order
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
            nodesorter = None
            for node in myNodes:
                if node.layer_name:
                    try:
                        nodesorter = '_'.join([layersort[node.layer_name],
                                           '%04d'%self.nodes[node]])
                    except:
                        if not node.layer_name:
                            pass
                        else:
                            pass
                elif not include_all:
                    continue
                else:
                    try:
                        nodesorter = '_'.join(['zzz', '%04d'%self.nodes[node]])
                        print "scene.get_ordered_nodes nolayer:", str(node), \
                                                                node.gname
                    except:
                        continue
                if nodesorter:
                    ordered_nodes[nodesorter] = node
            nodenums = ordered_nodes.keys()
            nodenums.sort()
            nodenums.reverse()
            for num in nodenums:
                nodelist.append(ordered_nodes[num])
        return nodelist
            
    def update_node(self, node, command=None):
        """update_node(node, command=None)
        
Update the PigScene's node tracking dict for node. Possible commands: 'Delete'
"""
        nodes = self.nodes
#        if _DEBUG: print "PigScene.update_node", node, command
        if not nodes.has_key(node):
#            if _DEBUG: print "   not registered:", node
            return
        else:
#            if  _DEBUG: print "   registered"
            node_num = nodes[node]
        if getattr(node,'deleted',False) or command == 'Delete':
            if nodes.has_key(node):
                try:
                    nodes.__delitem__(node)
#                    if _DEBUG: print "   deleted"
                except:
                    pass
#                    if _DEBUG: print "   could not delete (already gone?)"
#            else:
#                if _DEBUG: print "   unable to delete"
            return            
        # node_num tracks the order of node additions
        nodes[node] = node_num # this call sets off callbacks for nodes gui        
            
    def get_scene_layers(self):
        return get_available_layers()

    scene_layers = property(get_scene_layers, doc=
            'Utility property for viewing layers without __editor__ layer')
    
    @classmethod
    def _create_dummy(cls, exporter):
        # make sure we have our dummy node and cleanup registered
        if exporter_cleanup not in exporter.deleteCallbacks:
            exporter.register_delete_callback( exporter_cleanup)
        return cls()
    
    def _get_code_file(self):
        """_get_code_file(): return scene file with some special circumstances

If scene is unsaved, allow option to save it first. If not saved, return None.
If scene is a working scene, return 
"""
        if getattr(Opioid2D.Director, 'viewing_in_editor', False):
            import wx
            wx = wx
            interface = wx.GetApp().get_project_object()
            filename = interface.commit_scene()
            if not filename or Opioid2D.Director.scene.__class__ == PigScene:
                errorDlg = wx.MessageDialog( wx.GetApp().get_project_frame(),
                       "Your scene must be saved before viewing source.",
                       "Save Scene First",
                       wx.OK)
                errorDlg.ShowModal()
                errorDlg.Destroy() 
                return
            file = pug.BaseObject._get_code_file(self)
            if os.path.split(file)[1] == '__Working__.py':
                file = os.path.join(os.path.split(file)[0], filename)
            return file
        else:
            return pug.BaseObject._get_code_file(self)           
    
    # code storage customization
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if _DEBUG: print "*******************enter scene save"
        storage_name = storageDict['storage_name']
        if storage_name == 'PigScene' or storage_name == 'Scene':
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
            if self.nodes:
                # create ordered list of nodes
                nodes = self.get_ordered_nodes()
                nodes.reverse() # store them from bottom-most to top-most
                
                # store archetypes at top of file
                archetypes = False
                for node in nodes:
                    if not node.archetype:
                        continue
                    if not archetypes:
                        custom_code_list += [baseIndent, _INDENT*2, 
                                             '# Archetypes\n']
                        archetypes = True
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
                    archetype_exporter = save_object( node, savename)
                    if not archetype_exporter or \
                                            archetype_exporter.errorfilename:
                        error = ''.join(["PigScene code export failed...",
                                "unable to save archetype:",
                                savename, node])
                        warnings.warn(error)
                        return
                    module = __import__('.'.join(['objects',savename]),
                                       fromlist=[savename])
                    reload(module)
                    newclass = getattr(module,savename)
                    node.__class__ = newclass
                    nodeStorageDict = exporter.get_custom_storageDict(node)                            
                    nodeStorageDict['name'] =''.join([savename,'_archetype'])
                    nodeStorageDict['as_class'] = False # export as object
                    node_code = exporter.create_object_code(node, 
                                                            nodeStorageDict, 
                                                            indentLevel + 2,
                                                            False)                    
                    custom_code_list+=[node_code,'\n']
               
                # store instances
                instances = False
                for node in nodes:
                    if node.archetype:
                        continue
                    if not instances:
                        custom_code_list += [baseIndent, _INDENT*2, 
                                             '# Sprites\n']
                        instances = True
                    else:
                        custom_code_list +=['\n',]
                    nodeStorageDict = exporter.get_custom_storageDict(node)
                    nodeStorageDict['as_class'] = False # export as object
                    node_code = exporter.create_object_code(node, 
                                                            nodeStorageDict, 
                                                            indentLevel + 2,
                                                            False)                    
                    custom_code_list += [node_code]
            init_code = [baseIndent, _INDENT, 'def on_enter(self):\n']
            if not custom_code_list:
                custom_code_list = init_code
                custom_code_list += [baseIndent, _INDENT*2, 'pass\n']
            else:
                custom_code_list = init_code + custom_code_list
#            custom_code_list += [baseIndent, _INDENT*2, '# Pug auto-start\n']
#            custom_code_list += [baseIndent, _INDENT * 2, 'self.start()','\n']
        if base_code.endswith('pass\n') and custom_code_list: 
            # clean up pass case (for looks)
            base_code = base_code.splitlines()[0:-1]
            base_code.append('\n')
        else:
            base_code = [base_code +'\n']
        #add layers line
        layers = get_available_layers()
        if layers != ["Background"]:
            base_code += [baseIndent, _INDENT,'layers = ', str(layers),'\n']
        code = ''.join(base_code + custom_code_list)
        if _DEBUG: print "*******************exit scene save"
        return code
    
    _codeStorageDict = {
            'custom_export_func': _create_object_code,
            'as_class':True,
            'dummy_creator': '_create_dummy',
            'skip_attributes': ['_nodes','_groups','scene_layers','layers',
                                '_PigScene__node_num', '_key_down_dict', 
                                '_key_up_dict','started','k_info',
                                'mouse_manager']
             }   
    add_subclass_storageDict_key(_codeStorageDict, pug.BaseObject)

# force derived classes to use PigScene as base class
PigScene._codeStorageDict['base_class']=PigScene
# pug pugview stuff
            
def OnCollision(self, group1, group2, sprite1, sprite2):
    """Override so that the collision callback sig is:
callback( toSprite, fromSprite, toGroup, fromGroup)
"""
    try:
        sprite1 = ObjectManager.c2py(sprite1)
        sprite2 = ObjectManager.c2py(sprite2)
        func = self.scene._collision_handlers[group1,group2]
        func(sprite1, sprite2, group1, group2)
    except:
        traceback.print_exc(file=sys.stdout)
        raise
SceneCallbacks.OnCollision = OnCollision            
            
_scenePugview = {
    'name':'PigScene Editor',
    'skip_menus':['Export'],    
    'attributes':
    [
        ['Scene', pug.Label, {'font_size':10}],
        ['__class__', None, {'label':'   class', 'new_view_button':False}],        
        ['components'],
        ['scene_layers', SceneLayers],
#        ['scene_groups', SceneGroups],
#        ['scene_layers', None, {'label':'   layers','read_only':True}],
#        ['   Save Scene', pug.Routine, {'routine':save_scene, 
#                                        'use_defaults':True}],        
#        ['   Save Scene As', pug.Routine, {
#                               'routine':save_scene_as, 
#                               'use_defaults':True,
#                               'doc':"Save scene to disk with new name"}],        
        [' Scene Graph', pug.Label],
        ['nodes', SceneNodes, {'growable':True}],
    ]
}
pug.add_pugview('PigScene', _scenePugview, True)
