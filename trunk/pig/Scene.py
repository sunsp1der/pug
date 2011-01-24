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
from pig.util import entered_scene
from pig.editor.agui import SceneNodes, SceneLayers
from pig.editor.util import get_scene_layers, save_object, exporter_cleanup
from pig.keyboard import keys, keymods
from pig.PigDirector import PigDirector
from pig.gamedata import create_gamedata, get_gamedata
from pig.PigMouseManager import PigMouseManager

_DEBUG = False     

class Scene( OpioidScene, pug.BaseObject):
    """Scene - Scene with features for use with pug"""
    mouse_manager = None
    __node_num = 0
    started = False
    exitted = False
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
            if not getattr(PigDirector, 'project_started', False):
                gamedata = create_gamedata()
                gamedata.start_sceneclass = self.__class__
            for node in self.get_ordered_nodes():
                if node.archetype:
                    node.delete()
            if not getattr(PigDirector, 'project_started', False):
                self.on_project_start()
                self.all_nodes_callback( 'on_project_start')
                PigDirector.project_started = True
            self.all_nodes_callback( 'on_added_to_scene')
            self.all_nodes_callback( 'on_first_display')                        
            self.on_start()
            self.all_nodes_callback( 'on_scene_start')             
            self.started = True
        elif getattr(PigDirector, 'viewing_in_editor', False):
            # viewing in editor, not playing
            self.all_nodes_callback( 'on_added_to_editor')
        
    def register_node(self, node):        
#        """register(node): a new node is joining scene. Do callbacks"""
        if _DEBUG: print "Scene.register_node:",node,self.started
        if self.started:
            try:
                func = getattr(node, 'on_added_to_scene')
            except:
                pass
            else:
                func()
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
                func()
        self.nodes[node] = self.__node_num
        self.__node_num += 1        
        
    
    def all_nodes_callback(self, callback, *args, **kwargs):
        """Send a callback to all nodes in the scene"""
        if _DEBUG: print "Scene.all_nodes_callback:",callback,self.nodes.data
        nodes = self.nodes.copy()
        for node in nodes:
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
            if Opioid2D.Director.project_started:
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
        
Update the Scene's node tracking dict for node. Possible commands: 'Delete'
"""
        nodes = self.nodes
#        if _DEBUG: print "Scene.update_node", node, command
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
        return get_scene_layers()

    scene_layers = property(get_scene_layers, doc=
            "Scene layers excluding hidden ('__') layers")
    
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
            filename = interface.commit_scene()
            if not filename or Opioid2D.Director.scene.__class__ == Scene:
                errorDlg = wx.MessageDialog( wx.GetApp().get_project_frame(),
                       "Your scene must be saved before viewing source.",
                       "Save Scene First",
                       wx.OK)
                errorDlg.ShowModal()
                errorDlg.Destroy() 
                return
            file = pug.BaseObject._get_source_code(self)
            if os.path.split(file)[1] == '__Working__.py':
                file = os.path.join(os.path.split(file)[0], filename)
            return file
        else:
            return pug.BaseObject._get_source_code(self)
        
    def edit_code(self):
        "Edit the source file for this object"
        start_edit_process( self._get_source_code())    
        
    def _get_shell_info(self):
        "_get_shell_info()->info for pug's open_shell command"
        items = {'_Scene':self}
        nodes = self.nodes
        indexes = {}
        for node in nodes:
            name = node._get_shell_name()
            if name not in indexes:
                indexes[name]=1
            else:
                indexes[name]+=1
                name=name+"_"+str(indexes[name])
            items[name] = node
        items['_gamedata'] = get_gamedata()
        locals = items.copy()
        import pig.actions
        for action in dir(pig.actions):
            if action[0] != "_":
                locals[action]=getattr(pig.actions,action)
        return dict(rootObject=items,rootLabel="Scene Data",locals=locals,
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
                                '_PigScene__node_num', '_key_down_dict', 
                                '_key_up_dict','started','k_info',
                                'mouse_manager']
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