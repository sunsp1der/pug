from inspect import getmro
import time

from Opioid2D import Sprite, CallFunc, Delay
from Opioid2D.public.gui import GUISprite
from Opioid2D.public.Sprite import SpriteMeta

import pug
from pug.CallbackWeakKeyDictionary import CallbackWeakKeyDictionary
from pug.code_storage import add_subclass_storageDict_key
from pug.code_storage.constants import _INDENT, _PRETTIFY_FLOATS
from pug.util import make_valid_attr_name, prettify_path, prettify_float

from pig.PigDirector import PigDirector
from pig.editor.util import get_available_layers, save_object, \
                                exporter_cleanup, _fl_art_types

_DEBUG = False

class PigSprite(GUISprite, pug.BaseObject):
    """PigSprite( img=None, gname='')
    
Opioid2d Sprite with features for use with pug"""
    __metaclass__ = SpriteMeta
    _mouse_registered = False # can be "single", "multi", or "click"
    _image_file = None   
    _image = None
    _archetype = False
    destroy_blockers = None
    _pug_pugview_class = 'PigSprite'
    image = ''
    draggable = False
    auto_scene_register = True
    initialized = False
    
    def __del__(self):
        pug.BaseObject.__del__(self)
    
    def __init__(self, img=None, gname='', register=None):
        #_DEBUG = False #
        #if _DEBUG: print "PigSprite.__init__ 0"
        pug.BaseObject.__init__(self, gname=gname)
        #if _DEBUG: print "PigSprite.__init__ 1"
        Sprite._preinit(self, img)
        #if _DEBUG: print "PigSprite.__init__ 2"        
        self.collision_groups = set([])
        #if _DEBUG: print "PigSprite.__init__ 3"
        self.on_create()
        #if _DEBUG: print "PigSprite.__init__ 4"
        if register is None:
            register = self.auto_scene_register
        if register:
            self.scene_register()
        self.initialized = True
            
    def on_create(self):
        pass
            
    def mouse_register(self, type="multi"):
        """mouse_register(type): register for mouse events
        
type: 
    "single" means get all mouse events, and, if this sprite is the top gui 
        sprite, don't let any other sprites get mouse events
    "multi" means get all mouse events and let other sprites get mouse events
    "click" means only get drag, release, mousedown and mouseup events, and let 
        other sprites get mouse events
"""
        if self._mouse_registered != type:
            PigDirector.scene.mouse_manager.register(self, type)
            self._mouse_registered = type

    def mouse_unregister(self):
        """mouse_unregister(): unregister for mouse events"""
        if self._mouse_registered is not False:
            self._mouse_registered = False
            PigDirector.scene.mouse_manager.unregister(self)

    def on_collision(self, toSprite=None, fromSprite=None, toGroup=None, 
                     fromGroup=None, *a, **kw):
        """on_collision( toSprite, fromSprite, fromGroup, spriteGroup)
        
All arguments default to None.
toSprite: sprite that collided. Usually same as 'self' but included to match 
    Pig's callback system.
fromSprite: sprite we collided with
toGroup: group of this sprite that triggered this callback. This is useful
    when a sprite belongs to multiple groups
fromGroup: group of the sprite we collided with
Additional arguments are allowed, but will be ignored.

Callback for when object collides in gameplay.
This method is meant to work with the PigScene.register_collision_callback 
system. It does nothing in the base class, but is meant for overriding or for
stacking with pug.components.
"""
        pass

    def on_destroy(self):
        """on_destroy(): callback for when object is destroyed in gameplay"""
        pass
    
    def join_collision_group(self, group):
        "join_collision_group(group): join_group, add to self.collision_groups"
        self.collision_groups.add(group)
        self.join_group(group)
        
    def leave_collision_groups(self):
        "leave_collision_groups(): leave all collision groups"
        for group in self.collision_groups:
            Sprite.leave_group(self, group)
        self.collision_groups=set([])
        
    def leave_group(self, group):
        self.collision_groups.discard(group)
        Sprite.leave_group(self, group)
        
    def set_archetype(self, TF):
        """set_archetype( TF): set archetype property.
        
if TF is True create default gname. 
if TF is "True" set archetype to True, but don't create default name
""" 
        if TF == "True":
            self._archetype = True
        elif TF is True:
            if not self.gname:
                name = self.__class__.__name__
                superclasses = getmro(self.__class__)[1:]
                for cls in superclasses:
                    if name == cls.__name__ or name == 'Sprite' \
                                            or name == 'PigSprite':
                        name = ''.join(['My',name])    
                        break            
                name = make_valid_attr_name(name)
                self.gname = name
            self._archetype = True
        elif TF == False:
            self._archetype = False
    def get_archetype(self):
        return self._archetype
    archetype = property( get_archetype, set_archetype, 
                doc="Sprite used by editor. Does not appear in running scene.")
        
    def set_image(self, image):
        Sprite.set_image(self, image)
        if isinstance(image, basestring):
            self._image_file = image

    def set_image_file(self, file):
        if isinstance(file, basestring):
            self._image_file = file
        else:
            self._image_file = None
#        Sprite.set_image(self, file)
        if file is not None:
            (Delay(0) + CallFunc(Sprite.set_image, self, file)).do() 
    
    def get_image_file(self):
        # TODO: find a way to actually look up this filename in the image
        if self._image_file is None:
            try:
                image = self.get_image()._key[0]
                self._image_file = image._key[0]
            except:
                self._image_file = self._init_image
        return self._image_file
        # the following line had problems on windows:
        #     Sprite.set_image(self,image)
        # HACK: putting a Delay before the set_image fixes the problem...
#        if getattr(PigDirector, 'game_started', False):
#        else:
#            (Delay(0) + CallFunc(Sprite.set_image, self, image)).do()
        # HACK: but it slows down animations ALOT. wtf with this?!
        #Sprite.set_image(self,image)
        
    image_file = property(get_image_file, set_image_file, 
                          doc="The filename of this sprite's image")
    
    # scene management
    def _set_gname(self, value):
        pug.BaseObject._set_gname(self, value)
        if hasattr(PigDirector, '_scene'):
            if _DEBUG: print "PigSprite._set_gname calling scene.update_node"
            PigDirector.scene.update_node(self)
    gname = property( pug.BaseObject._get_gname, _set_gname, 
                      pug.BaseObject._del_gname,
                      "An easily accessed global name for this object")

    def destroy(self):
        """destroy(): set sprite up for deletion, but allow option to block
        
The destroy system is useful when dealing with deletion via components. When
destroy is called, the PigSprite will send an 'on_destroy' callback to itself.
Components (or an over-ridden on_destroy method) can then call 'block_destroy'
on the sprite, with the argument being the blocking object. This blocking is
cancelled when the blocking object is deleted or block_destroy(block=False) is 
called. When all blocks have been removed, 'delete' will be called.

In general, it is a good idea to use PigSprite.destroy rather than 
PigSprite.delete whenever the PigSprite is being removed by gameplay effects."""
        if _DEBUG:
            print 'PigSprite.destroy',self, self.destroy_blockers.data
        self.on_destroy()
        if self._mouse_registered :
            self.mouse_unregister()
        if not self.destroy_blockers:
            self.delete()
        
    def block_destroy(self, blocker, block=True, blockData=None):
        """block_destroy( blocker, block=True, blockData=None)
        
blocker: the object creating the block
block: set to False to unblock
blockData: optional info associated with blocker
        
block_destroy can be called before or during the 'on_destroy' callback. It will
add blocker to a dictionary of objects blocking the PigSprite's destruction."""
        if _DEBUG: 
            print 'PigSprite.block_destroy', self, blocker, block, blockData
        if block:
            if self.destroy_blockers is None:
                blockers = CallbackWeakKeyDictionary()
                blockers.register_for_delete( self.destroy_callback)
                self.destroy_blockers = blockers
            self.destroy_blockers[blocker] = blockData
        else:
            if blocker in self.destroy_blockers:
                self.destroy_blockers.pop(blocker)
                
    def destroy_callback(self, dict, func, arg1, arg2):
        if _DEBUG:
            print 'PigSprite.destroy_callback', dict, func, arg1, arg2
            print '    ', dict.data
        if not dict:
            if _DEBUG: print '    delete'
            self.destroy_blockers.unregister( self.destroy_callback)
            self.delete()        

    def delete(self):
        if self._mouse_registered :
            self.mouse_unregister()
        PigDirector.scene.update_node(self, "Delete") # register self with scene                
        Sprite.delete(self)
        
    def set_tint(self, tint):
        """set_tint( tint)
 
tint: a tuple or list of 3 or 4 elements- (red, green, blue, [alpha])
    the alpha element will be ignored. Use set_alpha or to set that."""
        color = (tint[0]/255.0, tint[1]/255.0, tint[2]/255.0, self.get_alpha())
        Sprite.set_color( self, color)
        
    def get_tint(self):
        "get_tint()->the (red, green, blue) color value of the sprite"
        color = Sprite.get_color( self)
        return (int(round(color[0]*255.0)), int(round(color[1]*255)), 
                int(round(color[2]*255)))
    
    tint = property(get_tint, set_tint, doc="The color tint of the sprite")
    
    def scene_register(self):
        "scene_register(): register with the PigScene"
        PigDirector.scene.register_node(self)        

    # layer_name property
    def set_layer(self, layer):
        if layer not in PigDirector.scene.layers:
            PigDirector.scene.add_layer(layer)
        Sprite.set_layer(self, layer)
        if _DEBUG: print "PigSprite.set_layer calling scene.update_node"
        PigDirector.scene.update_node(self) # register self with scene    
    def get_layer_name(self):
        try:
            return self.layer.name
        except:
            return ''
    layer_name =  property(get_layer_name, set_layer, 
                           doc="Name of scene layer")
    
    def save_sprite(self):
        """Save this object as a class in the project's object folder"""
        save_object( self)
        
    def _get_code_file(self):
        "_get_code_file(): return the scene file if this is not a derived class"
        if self.__class__ == PigSprite:
            return PigDirector.scene._get_code_file()
        else:
            return pug.BaseObject._get_code_file(self)   
    
    # code storage customization
    @classmethod
    def _create_dummy(cls, exporter):
        # make sure we have our dummy node and cleanup registered
        dummy = None
        print "PigSprite.createdummy 0"
        if exporter_cleanup not in exporter.deleteCallbacks:
            exporter.register_delete_callback( exporter_cleanup)
        print "PigSprite.createdummy 1", cls
        dummy = cls(register=False)
        print "PigSprite.createdummy 2"
        t = 0     
        while not dummy.initialized:
            t = t+1
            print " PigSprite.createdummy wait", t
            time.sleep(0.02)
            if t == 50:
                return None
        return dummy
        
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if _DEBUG: print "*******************enter sprite save: "+str(self)        
        # check for valid names
        storage_name = storageDict['storage_name']
        if storage_name == 'PigSprite' or storage_name == 'Sprite':
            raise ValueError(''.join(["Can't over-write ",
                                      storage_name," base class."]))
        # grandchildren need to call their parent.on_create
        if storageDict['base_class'].__name__ != 'PigSprite':
            storageDict = storageDict.copy()
            storageDict['base_init'] = True
        # clean up
        self.rotation = self.rotation % 360
        # export code
        code = []
        info = (self, storageDict, indentLevel) # for convenience
        code.append(exporter.create_instantiator_code(*info))
        base_code = exporter.create_base_code(*info)
        # custom code
        baseIndent = _INDENT * indentLevel    
        dummy = exporter.dummyDict.get(storageDict['base_class'], None)
        custom_code = []
        if storageDict['as_class']:
            if not dummy or dummy.image_file != self.image_file:
                custom_code += [baseIndent, _INDENT, 'image = ', 
                                repr(prettify_path(self.image_file)),'\n']
            if not dummy or dummy.layer_name != self.layer_name:
                custom_code += [baseIndent, _INDENT, 'layer = ', 
                                repr(self.layer_name),'\n']
            init_def = exporter.create_init_method(docode=False, *info)
            custom_code += [init_def]
            xIndent = _INDENT * 2
            name = 'self'
        else:
            name = storage_name
            if not dummy or dummy.image_file != self.image_file:
                custom_code += [baseIndent, name, '.image = ', 
                                    repr(prettify_path(self.image_file)),'\n']
            if not dummy or dummy.layer_name != self.layer_name:
                custom_code += [baseIndent, name, '.layer = ', 
                                    repr(self.layer_name),'\n']
            xIndent = ''
        # instance attributes
        custom_attr_code = []
        vectorList = [('acceleration', (0, 0)),
                      ('position', (0, 0)),
                      ('scale', (1.0, 1.0)),
                      ('velocity', (0, 0))]
        prefix = ''.join([baseIndent, xIndent, name, '.'])
        for attr, default in vectorList:
            vector = getattr(self, attr)
            if not dummy or \
                    getattr(dummy, attr).radial != getattr(self,attr).radial:
                if _PRETTIFY_FLOATS:
                    # get rid of long strings of zeros or nines
                    axes = [prettify_float(vector.x), 
                            prettify_float(vector.y)]
                    custom_attr_code += [prefix, 
                                     attr, ' = (', axes[0],
                                     ', ', axes[1],')','\n']
                else:
                    custom_attr_code += [prefix, 
                                     attr, ' = (', repr(vector.x),
                                     ', ', repr(vector.y),')','\n']
        custom_code += custom_attr_code
        if storageDict['as_class']:
            init_code = exporter.create_init_method(dodef=False, *info)
            custom_code.append(init_code)          
            if not custom_code:
                init_code = ''.join([baseIndent,  xIndent, 'pass\n'])  
        code += custom_code
        if not base_code.endswith('pass\n'): # clean up pass case (for looks)
            code.append(base_code)
        if _DEBUG: print "*******************exit sprite save: "+str(self)        
        return ''.join(code)
#    def test(self):
#        import cOpioid2D as _c
#        self._image._cObj.hotspot = _c.Vec2(0,0)
#        print self._image._cObj.hotspot.x, self._image._cObj.hotspot.y 
#        return self._image._cObj
    
    _codeStorageDict = {
            'skip_attributes': ['_actions', '_image_file', 'image_file','color',
                                'layer_name','_init_image','_init_layer',
                                'register', 'destroy_blockers', '_archetype',
                                'draggable', 'auto_scene_register', 
                                '_mouse_registered'], 
            'instance_attributes': ['*'],
            'instance_only_attributes':['gname'],
            'init_method':'on_create',
            'init_method_args': [],
            'base_init': False,
            'force_init_def': True,
            'dummy_creator': '_create_dummy',
            'custom_export_func': _create_object_code,
            'as_class': True,
                        }
    add_subclass_storageDict_key(_codeStorageDict, pug.BaseObject) 

# force derived classes to use PigSprite as a base. Advanced users can get
# around this however they need to
# PigSprite._codeStorageDict['base_class'] = PigSprite

        
_spritePugview = {
    'name':'PigSprite Editor',
    'skip_menus':['Export'],
    'attributes':
    [
        ['Sprite', pug.Label, {'font_size':10}],
        ['__class__', None, {'label':'   class', 'new_view_button':False}],
        ['gname'],
        ['archetype', 
                '\n'.join(["Select this to automatically save this sprite",
                           "to the objects folder when the scene is saved.",
                           "It will not appear in the scene when running."])],
        ['save_sprite', None, {'label':'   Save Object',
                               'use_defaults': True}],
        [' Components', pug.Label],
        ['components'],
        [' Image', pug.Label],
        ['image_file', pug.ImageBrowser, {'subfolder':'art', 
                                          'filter':_fl_art_types}],
        ['tint', pug.ColorPicker,{'text_control':True}],
        ['alpha'],
        [' Spacial', pug.Label],
        ['layer_name', pug.Dropdown, {'list_generator':get_available_layers,
                                      'label':'   layer'}],
        ['position'],
        ['rotation'],
        ['scale'],
#        ['lighting'],
    #        ['', Label, {'label':' Groups'}],
    #        ['group', Dropdown, 
    #                      'list_generator':get_available_groups,
    #                      }],
    #        ['', pug.Label, {'label':' Physics'}],
    #        ['rotation_speed'],
    #        ['velocity'],
    #        ['acceleration'],
        [' Functions', pug.Label],
        ['delete',"Delete this sprite"],
    #        ['_delete_test'],
    ]       
 }
pug.add_pugview('PigSprite', _spritePugview, True)
########################################################
## reveal this to test PigSprite deletion problems
_spritePugview['attributes'].append(['test_referrers'])
from pug.util import test_referrers
def _test_referrers( self):
    test_referrers(self)
PigSprite.test_referrers = _test_referrers
####################################################
if hasattr(PigSprite,'test'):
    _spritePugview['attributes'].append(['test'])


