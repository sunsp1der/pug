from Opioid2D import Sprite, Director, CallFunc, Delay
from Opioid2D.public.Sprite import SpriteMeta

import pug
from pug.CallbackWeakKeyDictionary import CallbackWeakKeyDictionary
from pug.syswx.attributeguis import *
from pug.code_storage import add_subclass_skip_attributes
from pug.code_storage.constants import _INDENT
from pig.editor.util import get_available_layers, save_object, \
                                exporter_cleanup


_DEBUG = False

class PigSprite(Sprite, pug.BaseObject):
    """PigSprite( img=None, gname='')
    
Opioid2d Sprite with features for use with pug"""
    __metaclass__ = SpriteMeta
    _image_file = None   
    archetype = False
    destroy_blockers = None
    _pug_pugview_class = 'PigSprite'
    
    def __del__(self):
        pug.BaseObject.__del__(self)
    
    def __init__(self, img=None, gname='', register=True):
        pug.BaseObject.__init__(self, gname=gname)
        Sprite._preinit(self, img)
        self.on_create()
        if register:
            self.do_register()
        
    def set_image(self, image):
        if isinstance(image, basestring):
            self._image_file = image
        Sprite.set_image(self, image)

    def set_image_file(self, file):
        self._image_file = file
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
#        if getattr(Director, 'game_started', False):
#        else:
#            (Delay(0) + CallFunc(Sprite.set_image, self, image)).do()
        # HACK: but it slows down animations ALOT. wtf with this?!
        #Sprite.set_image(self,image)
        
    image_file = property(get_image_file, set_image_file)
    
    # scene management
    def _set_gname(self, value):
        pug.BaseObject._set_gname(self, value)
        if hasattr(Director, '_scene'):
            if _DEBUG: print "PigSprite._set_gname calling scene.update_node"
            Director.scene.update_node(self)
    gname = property( pug.BaseObject._get_gname, _set_gname, 
                      pug.BaseObject._del_gname,
                      "An easily accessed global name for this object")

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

This method is meant to work with the PigScene.register_collision_callback 
system. It does nothing in the base class, but is meant for overriding or for
stacking with pug.components.
"""
        pass
#        print "on_collision", self, toSprite, fromSprite, toGroup, fromGroup

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
        self.on_destroy()
        
    def on_destroy(self):
        """on_destroy(): callback for when object is destroyed in gameplay"""
        if _DEBUG:
            print 'PigSprite.on_destroy',self, self.destroy_blockers.data
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
            self.delete()        

    def delete(self):
        Director.scene.update_node(self, "Delete") # register self with scene                
        Sprite.delete(self)
        
    def do_register(self):
        "do_register(): register with the PigScene"
        Director.scene.register_node(self)        

    # layer_name property
    def set_layer(self, layer):
        if layer not in Director.scene.layers:
            Director.scene.add_layer(layer)
        Sprite.set_layer(self, layer)
        if _DEBUG: print "PigSprite.set_layer calling scene.update_node"
        Director.scene.update_node(self) # register self with scene    
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
    
    # code storage customization
    @classmethod
    def _create_dummy(cls, exporter):
        # make sure we have our dummy node and cleanup registered
        if exporter_cleanup not in exporter.deleteCallbacks:
            exporter.register_delete_callback( exporter_cleanup)
        return cls(register=False)
        
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if _DEBUG: print "*******************enter sprite save: "+str(self)        
        # check for valid names
        storage_name = storageDict['storage_name']
        if storage_name == 'PigSprite' or storage_name == 'Sprite':
            raise ValueError(''.join(["Can't over-write ",
                                      storage_name," base class."]))
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
                                repr(self.image_file),'\n']
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
                                    repr(self.image_file),'\n']
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
                custom_attr_code += [prefix, 
                                     attr, '.', 'x = ', repr(vector.x),'\n']
                custom_attr_code += [prefix, 
                                     attr, '.', 'y = ', repr(vector.y),'\n']
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
    
    _codeStorageDict = {
            'skip_attributes': ['_actions', '_image_file', 'image_file', 
                                'layer_name','_init_image','_init_layer',
                                'register', 'destroy_blockers'], 
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
    add_subclass_skip_attributes(_codeStorageDict, pug.BaseObject)    

#    def test(self):
#        self.set_image("art/button.png")
# force derived classes to use PigSprite as a base
#PigSprite._codeStorageDict['base_class'] = PigSprite

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
                           "It will not appear in the game."])],
        ['save_sprite', None, {'label':'   Save Object',
                               'use_defaults': True}],
        [' Spacial', pug.Label],
        ['layer_name', pug.Dropdown, {'list_generator':get_available_layers,
                                      'label':'   layer'}],
        ['position'],
        ['rotation'],
        ['scale'],
        [' Image', pug.Label],
        ['image_file', pug.ImageBrowser],
        ['color'],
        ['lighting'],
    #        ['', Label, {'label':' Groups'}],
    #        ['group', Dropdown, 
    #                      'list_generator':get_available_groups,
    #                      }],
    #        ['', pug.Label, {'label':' Physics'}],
    #        ['rotation_speed'],
    #        ['velocity'],
    #        ['acceleration'],
        [' Components', pug.Label],
        ['components'],
        [' Functions', pug.Label],
        ['delete',"Delete this sprite"],
    #        ['_delete_test'],
    #        ['_test_referrers'],
    ]       
 }

if hasattr(PigSprite,'test'):
    _spritePugview['attributes'].append(['test'])

pug.add_pugview('PigSprite', _spritePugview, True)