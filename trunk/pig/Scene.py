import os.path
from weakref import WeakKeyDictionary
import warnings
import sys
import traceback
import time

from pygame.locals import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.key import get_pressed, get_mods

import Opioid2D
from Opioid2D import Scene as OpioidScene
from Opioid2D.internal.objectmgr import ObjectManager
from Opioid2D.public.Scene import SceneCallbacks

import pug
from pug.CallbackWeakKeyDictionary import CallbackWeakKeyDictionary
from pug.code_storage.constants import _INDENT
from pug.code_storage import add_subclass_storageDict_key
from pug.util import make_valid_attr_name, start_edit_process

from pig.PauseState import PauseState
from pig.editor.agui import SceneNodes, SceneLayers
from pig.editor.util import get_scene_layers, save_object, exporter_cleanup,\
                            entered_scene
from pig.keyboard import keys, keymods
from pig.PigDirector import PigDirector
from pig.gamedata import create_gamedata, get_gamedata
from pig.PigMouseManager import PigMouseManager

_DEBUG = False     

class Scene( OpioidScene, pug.BaseObject):
    """Scene - Scene with features for use with pug"""
    mouse_manager = None
    started = False
    exitted = False
    switching = False
    switch_blockers = None
    _pug_pugview_class = 'Scene'
    layers = ['Background']
    k_info = []
    keys_pressed = None # efficiency for key register double-check
    def __init__(self, gname=''):
        if _DEBUG: print "do Scene.__init__",self
        self._key_down_dict = {}
        self._key_up_dict = {}
        self._collision_callback_dict = WeakKeyDictionary()
            # 2D dict by sprite, then (collide-with-Group, this-sprite-Group)
        self.k_info = [self.register_key_up(keys["ESCAPE"], self.keypause),
                       self.register_key_up((keymods["CTRL"],
                                               keys["Q"]), self.keyquit)]
        OpioidScene.__init__(self)
        pug.BaseObject.__init__(self, gname)   
        if _DEBUG: print "Scene.__init__ done", self.__class__.__name__ 
        
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
        callback_dict = collision_dict.get(toSprite, None)
        if callback_dict is not None:
            for groups, callbacks in callback_dict.iteritems():
                
                if self._groups.get( groups[1]) and \
                            fromSprite in self._groups.get( groups[1]):
                    for callback in callbacks:
                        callback( toSprite, fromSprite, groups[0], groups[1])
        # we only get one callback, so check if fromSprite needs a call
        # this is slow and could possibly be improved
        if check_reverse:
            self.collide_callbacker( fromSprite, toSprite, fromGroup, toGroup, 
                                   False)
        
    def unregister_collision_callback(self, sprite, 
                                      toGroup=None, fromGroup=None): 
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
        

    def do_key_callbacks(self, key, mod=0, keydict="KEYDOWN", a=None, kw=None):
        """do_key_callbacks(key, mod=0, keydict="KEYDOWN", a=None, kw=None)
        
key = key number
mod = key mod number
keydict = dictionary of callbacks or "KEYUP" or "KEYDOWN" 
a = arguments to be prepended to callback arguments
kw = keyword arguments to update callback arguments
"""
        if a is None:
            a = tuple()
        if kw is None:
            kw = {}
        if type(keydict) != dict:
            if keydict == "KEYUP":
                keydict = self._key_up_dict
            elif keydict == "KEYDOWN":
                keydict = self._key_down_dict
            else:
                raise ValueError("No callback dict named '" + keydict + "'")
        fn_list = keydict.get((mod, key), [])
        for fn_info in fn_list: 
            newa = a + fn_info[1]
            newkw = fn_info[2].copy()
            newkw.update(kw)
            fn_info[0]( *newa, **newkw)

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
        self.do_key_callbacks(key, mod, dict)

    def register_key_down(self, key, fn, *args, **kwargs):
        """register_key_down(key, fn, *args, **kwargs)
    
Register a function to execute when a given key is pressed. If the key is being
pressed when this is registered, the function will be executed immediately
unless the kwarg _do_immediate is set to False.
key: can be either a keys[] constant (or index) from pig.keyboard or a tuple in 
    the form (keymods[] constant/index, keys[] constant/index)
fn: the function to call when the keypress occurs
*args, **kwargs: arguments to fn    
"""
        # if key is already down, perform function
        if kwargs.pop('_do_immediate', True):
            try:
                if type(key) is tuple:
                    if type(key[0]) is str:
                        keymod = keymods[key[0]]
                    else:
                        keymod = key[0]
                    if type(key[1]) is str:
                        thekey = keys[key[1]]
                    else:
                        thekey = key[1]
                if type(key) is str:
                    thekey = keys[key]
                    keymod = 0
                pressed = get_pressed()[thekey]
                if pressed:
                    mods = get_mods() & ~4096
                    if keymod is 0:
                        if mods:
                            pressed = False
                    else:
                        if not (keymod & mods):
                            pressed = False
            except:
                pass
            else:
                if pressed:
                    fn(*args,**kwargs)
        return self._register_key( self._key_down_dict, key, fn, 
                                   *args, **kwargs)
        
    def register_key_up(self, *args, **kwargs):
        """register_key_up(key, fn, *args, **kwargs)

Like register_key_down, but when key is released"""
        return self._register_key( self._key_up_dict, *args, **kwargs)

    def unregister_key_down(self, key, fn=None, *args, **kwargs):
        """unregister_key_down(key, fn=None, *args, **kwargs)
    
Unregister a function to execute when a given key is pressed. Returns True if fn
is found. If no function is specified, unregister that key altogether and return
True.
key: can be either a keys[] constant (or index) from pig.keyboard or a tuple in 
    the form (keymods[] constant/index, keys[] constant/index)
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

key: can be either a keys[] constant (or index) from pig.keyboard or a tuple in 
    the form (keymods[] constant/index, keys[] constant/index)
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
                if type(keymod) is not int: 
                    keymod = keymods[keymod]
                key = key[1]
                if type(key) is not int: 
                    key = keys[key]
            except:
                # key must just be a keymode
                keymod = 0
                if type(key) is not int: 
                    key = keys[key]
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
                import wx
                wx.CallAfter(entered_scene)
            except:
                pass
        self.on_enter()
        self.start()
        
    def start(self):
        """start()

Start the scene running. Called after enter() and before state changes
"""
        if _DEBUG: print "start 0"
        if getattr(PigDirector, 'start_project', False):
            if not getattr(PigDirector, 'project_started', False):
                gamedata = create_gamedata()
                gamedata.start_sceneclass = self.__class__
            if _DEBUG: print "start 1"
            for node in self.nodes.keys():
                if node.archetype:
                    node.delete()
            if _DEBUG: print "start 2"
            if not getattr(PigDirector, 'project_started', False):
                self.on_project_start()
                self.all_nodes_callback( 'on_project_start')
                PigDirector.project_started = True
            if _DEBUG: print "start 3"
            self.all_nodes_callback( 'on_added_to_scene')
            self.all_nodes_callback( 'on_first_display')                        
            self.on_start()
            self.all_nodes_callback( 'on_scene_start')             
            self.started = True
            if _DEBUG: print "start 4"
        elif getattr(PigDirector, 'viewing_in_editor', False):
            # viewing in editor, not playing
            self.all_nodes_callback( 'on_added_to_editor')
        if _DEBUG: print "start 5"
        
    def register_node(self, node):        
#        """register(node): a new node is joining scene. Do callbacks"""
        if _DEBUG: print "Scene.register_node:",node,self.started
        if self.started:
            if hasattr(node, 'on_added_to_scene'):
                node.on_added_to_scene()
            if hasattr(node, 'on_first_display'):
                node.on_first_display()
        elif getattr(PigDirector, 'editorMode', False):
            if hasattr(node, 'on_added_to_editor'):
                node.on_added_to_editor()
        self.nodes[node] = int(node._cObj.this)        
    
    def all_nodes_callback(self, callback, *args, **kwargs):
        """Send a callback to all nodes in the scene"""
        if _DEBUG: print "Scene.all_nodes_callback:",callback,self.nodes.data
        for node in self.nodes.keys():
            try:
                func = getattr(node, callback)
            except:
                pass
            else:
#                if _DEBUG: print "Scene.node_callback",callback,node
                func( *args, **kwargs)
                        
    def on_start(self):
        """Callback hook for when scene starts playing"""
        pass

    def on_enter(self):
        pass
    
    def on_project_start(self):
        """Callback hook for when project starts with this scene"""
        pass
    
    def on_exit(self):
        """Callback hook for when scene is exitted"""
        pass
    
    def on_switch_scene(self, scene=None):
        """on_switch_scene(self, scene=None)

Callback hook when a request is received to switch away from this scene. Use the
block_switch_scene method to delay switch during clean up and/or scene exit 
effects.

scene: the scene about to be switched to
"""
        pass
    
    def switch_scene_to(self, scene):
        "Called by director when a request is received to switch scenes"
        if not self.switching:
            self.on_switch_scene(scene)
            self.switching = True
            self.switch_scene = scene 
        if not self.switch_blockers:
            PigDirector.set_scene( scene)
            
    def block_switch_scene(self, blocker, block=True, blockData=None):
        """block_switch_scene( blocker, block=True, blockData=None)
        
blocker: the object creating the block
block: set to False to unblock
blockData: optional info associated with blocker
        
block_switch_scene can be called before or during the 'on_switch_scene' 
callback. It will add blocker to a dictionary of objects blocking the switching
of the scene."""
        if _DEBUG: 
            print 'Scene.block_switch_scene', self, blocker, block, blockData
        if block:
            if self.switch_blockers is None:
                blockers = CallbackWeakKeyDictionary()
                blockers.register_for_delete( self.switch_blocker_callback)
                self.switch_blockers = blockers
            self.switch_blockers[blocker] = blockData
        else:
            if blocker in self.switch_blockers:
                self.switch_blockers.pop(blocker)

    def switch_blocker_callback(self, dict, func, arg1, arg2):
        if _DEBUG:
            print 'Scene.switch_blocker_callback', dict, func, arg1, arg2
            print '    ', dict.data
        if not dict:
            if _DEBUG: print '    switch'
            self.switch_blockers.unregister( self.switch_blocker_callback)
            PigDirector.set_scene( self.switch_scene)       
    
    def stop(self):
        """Stop a level that is playing"""
        self.exit()
        Opioid2D.Director.project_started = False  
        Opioid2D.Director.start_project = False                     
        self.started = False
        
    def exit(self):
        if _DEBUG: print "Scene.exit"
        if not self.exitted:
            #if _DEBUG: 
            if _DEBUG: print "do Scene.exit", self
            if PigDirector.project_started:
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

    nodes = property (_get_nodes,
                      doc="dictionary of Scene nodes:int(node._cObj)")

    def get_ordered_nodes(self):
        """get_ordered_nodes()->list of nodes sorted top to bottom 
        
Return a list of scene nodes, sorted by layer then order within the layer.
"""
 #       nodelist = []
        if self.nodes:
            # create ordered list of nodes
            layers = self.get_scene_layers()[:]
#            layerinfo = {} # layerinfo[layer] = (sort#, nodelist)
#            a = 1
            ordered_nodes = []
            keys = self.nodes.keys()
            values = self.nodes.values()
            for layer in layers:
                l = PigDirector.scene.get_layer(layer)
                node_ids = list( int(ptr.this) for ptr in l._layer.GetNodes())
                for id in node_ids:
                    idx = values.index(id)
                    ordered_nodes.append(keys[idx])
            ordered_nodes.reverse()                    
            return ordered_nodes
        else:
            return[]
            
    def update_node(self, node, command=None):
        """update_node(node, command=None)
        
Update the Scene's node tracking dict for node. Possible commands: 'Delete'
"""
        nodes = self.nodes
#        if _DEBUG: print "Scene.update_node", node, command
        if not nodes.has_key(node):
#            if _DEBUG: print "   not registered:", node
            return
        if getattr(node,'deleted',False) or command == 'Delete':
            try:
                nodes.__delitem__(node)
            except:
                pass
            return            
        # node_num tracks the order of node additions
        nodes[node] = int(node._cObj.this) 
        # this call sets off callbacks for nodes gui        
            
    def get_scene_layers(self):
        return get_scene_layers()

    scene_layers = property(get_scene_layers, doc=
            "Scene layers excluding hidden ('__') layers")
    
    def add_layer(self, name, skip_hidden=True):
        """add_layer(name, skip_hidden=True)
        
Add a layer to the scene.
name: name of layer
skip_hidden: layers are always added at top. If this is True, the layer will be
added under hidden layers (names begin with '__') which are generally used by 
the editor. If layer is hidden, this will be ignored."""
        if name[0:1] == '__' or not skip_hidden or self.layers == [] or \
                PigDirector.scene is None:
            return Opioid2D.Scene.add_layer( self, name)
        layerlist = self.scene_layers
        last_layer = layerlist[-1]
        Opioid2D.Scene.add_layer(self, name)
        # we need to avoid hidden layers
        c_layers = self.get_c_layers()
        idx = 0
        for c_layer in c_layers:
            if c_layer.GetName() == last_layer:
                break
            idx += 1
        self.move_layer( name, -(len(c_layers) - idx - 2))
       
    @classmethod
    def _create_dummy(cls, exporter):
        # make sure we have our dummy node and cleanup registered
        if exporter_cleanup not in exporter.deleteCallbacks:
            exporter.register_delete_callback( exporter_cleanup)
        return cls()
    
    def _get_source_code(self):
        """_get_source_code(): return scene file with some special circumstances

If scene is unsaved, allow option to save it first. If not saved, return None.
If scene is a working scene, return 
"""
        if getattr(Opioid2D.Director, 'viewing_in_editor', False):
            import wx
            wx = wx
            interface = wx.GetApp().get_project_object()
            saved = interface.check_save(message="Scene has changed.\n"+\
                                         "Save scene before viewing code?")
            if Opioid2D.Director.scene.__class__ == Scene:
                errorDlg = wx.MessageDialog( wx.GetApp().get_project_frame(),
                       "Your scene must be saved before viewing source.",
                       "Save Scene First",
                       wx.OK)
                errorDlg.ShowModal()
                errorDlg.Destroy() 
                return
            file = pug.BaseObject._get_source_code(self)
            return file
        else:
            return pug.BaseObject._get_source_code(self)
        
    def edit_code(self):
        "Edit the source file for this object"
        start_edit_process( self._get_source_code())    
        
    def _get_shell_info(self):
        "_get_shell_info()->info for pug's open_shell command"
        rootObject = self
        rootLabel = self.__class__.__name__
        locals={}
        locals['_gamedata'] = get_gamedata()
        locals[rootLabel] = self
        import pig.actions
        for action in dir(pig.actions):
            if action[0] != "_":
                locals[action]=getattr(pig.actions,action)
        return dict(rootObject=rootObject,rootLabel=rootLabel,locals=locals,
                    pug_view_key=self)
        
    # code storage customization
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if _DEBUG: print "*******************enter scene save"
        storage_name = storageDict['storage_name']
        if storage_name == 'Scene' or storage_name == 'Scene':
            raise ValueError(''.join(["Can't over-write ",
                                      storage_name," base class."]))
        if not storageDict['as_class']:            
            raise ValueError("Scenes can only be stored as classes.")
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
                    savename = make_valid_attr_name(node.gname)
                    node.gname = savename
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
                    error = ''.join(["Scene code export failed...",
                            "unable to save archetype:",
                            savename, node])
                    warnings.warn(error)
                    return
                time.sleep(0.1)
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
        #spacing before custom code
        if custom_code_list:
            custom_code_list = ['\n']+custom_code_list
        #add layers line
        layers = get_scene_layers()
        if layers != ["Background"]:
            layercode = ''.join([baseIndent, _INDENT,'layers = ', str(layers),
                                '\n'])
            base_code_lines = base_code.splitlines()
            base_code = '\n'.join([base_code_lines[0]] + [layercode] +\
                                  base_code_lines[1:])+'\n'
        # remove pass in base code if we have custom code
        if base_code.endswith('pass\n') and custom_code_list: 
            # clean up pass case (for looks)
            base_code = '\n'.join(base_code.splitlines()[0:-1])
        code = ''.join([base_code] + custom_code_list)
        if _DEBUG: print "*******************exit scene save"
        return code
    
    _codeStorageDict = {
            'custom_export_func': _create_object_code,
            'as_class':True,
            'dummy_creator': '_create_dummy',
            'init_method':'on_enter',
            'init_method_args':[],
            'base_init': False,
            'force_init_def': True,
            'skip_attributes': ['_nodes','_groups','scene_layers','layers',
                                '_key_down_dict', '_key_up_dict','started',
                                'k_info', 'mouse_manager']
             }   
    add_subclass_storageDict_key(_codeStorageDict, pug.BaseObject)

# force derived classes to use Scene as base class
Scene._codeStorageDict['base_class']=Scene
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
    'name':'Scene Editor',
    'skip_menus':['Export'],   
    'attributes':
    [
        ['Scene', pug.Label, {'font_size':10}],
        ['__class__', None, {'label':'   class', 'new_view_button':False}],        
        ['components'],
##        ['components', pug.ComponentFolder],
        [' Scene Layers', pug.Label],
        ['scene_layers', SceneLayers],
#        ['edit_code', None, {'label':'   Edit code'}],        
#        ['   Save Scene', pug.Routine, {'routine':save_scene, 
#                                        'use_defaults':True}],        
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
pug.add_pugview('Scene', _scenePugview, True)
