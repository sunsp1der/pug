import gc

from Opioid2D import Sprite, Director, Delete
from Opioid2D.public.Node import Node
from Opioid2D.public.Sprite import SpriteMeta

import pug
from pug.syswx.attributeguis import *
from pug.code_storage import add_subclass_skip_attributes
from pug.code_storage.constants import _INDENT
from pug_opioid.editor.util import get_available_layers, save_object, \
                                exporter_cleanup

import sys

DEBUG = False

class PugSprite(Sprite, pug.BaseObject):
    """PugSprite( img=None, gname='')
    
Opioid2d Sprite with features for use with pug
"""
    __metaclass__ = SpriteMeta
    _pug_template_class = 'PugSprite'
    # image stuff... allows entry and storage of filename
    _image_file = None   
    is_template = False
    def __init__(self, img=None, gname=''):
        pug.BaseObject.__init__(self, gname=gname)
        Sprite.__init__(self, img)
    def get_image_file(self):
        # TODO: find a way to actually look up this filename in the image
        if self._image_file is None:
            self._image_file = self._init_image
        return self._image_file
    def set_image(self, image):
        if isinstance(image, basestring):
            self._image_file = image
        Sprite.set_image(self,image)
    image_file = property(get_image_file, set_image)
    
    # scene management
    def _set_gname(self, value):
        pug.BaseObject._set_gname(self, value)
        if DEBUG: print "PugSprite._set_gname callimg scene.update_node"
        Director.scene.update_node(self)
    gname = property( pug.BaseObject._get_gname, _set_gname, 
                      pug.BaseObject._del_gname,
                      "An easily accessed global name for this object")

    def _on_mgr_delete(self):
        Sprite._on_mgr_delete(self)  
        if DEBUG: print "PugSprite._on_mgr_delete calling scene.update_node"
        Director.scene.update_node(self, "Delete") # register self with scene                

    # layer_name property
    def set_layer(self, layer):
        if layer not in Director.scene.layers:
            Director.scene.add_layer(layer)
        Sprite.set_layer(self, layer)
        if DEBUG: print "PugSprite.set_layer calling scene.update_node"        
        Director.scene.update_node(self) # register self with scene    
    def get_layer_name(self):
        try:
            return self.layer.name
        except:
            return ''
    layer_name =  property(get_layer_name, set_layer, 
                           doc="Name of scene layer")
    
    def save_sprite(self):
        """Save this object as a class in the project's sprite folder"""
        save_object( self)
    
    # code storage customization
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if DEBUG: print "*******************enter sprite save: "+str(self)        
        # make sure we have our dummy node cleanup registered
        if exporter_cleanup not in exporter.deleteCallbacks:
            exporter.register_delete_callback( exporter_cleanup)
        # check for valid names
        storage_name = storageDict['storage_name']
        if storage_name == 'PugSprite' or storage_name == 'Sprite':
            raise ValueError(''.join(["Can't over-write ",
                                      storage_name," base class."]))
        # clean up
        self.rotation = self.rotation % 360
        # export code
        code = []
        info = (self, storageDict, indentLevel) # for convenience
        code.append(exporter.create_instantiator_code(*info))
        base_code = exporter.create_base_code(*info)
        dummy = exporter.dummyDict.get(storageDict['base_class'], None)
        if not base_code.endswith('pass\n'): # clean up pass case (for looks)
            code.append(base_code)
        # custom code
        baseIndent = _INDENT * indentLevel    
        hasAttrs = False    
        custom_code = []
        if storageDict['as_class']:
            if not dummy or dummy.image_file != self.image_file:
                custom_code += [baseIndent, _INDENT, 'image = ', 
                                repr(self.image_file),'\n']
            if not dummy or dummy.layer_name != self.layer_name:
                custom_code += [baseIndent, _INDENT, 'layer = ', 
                                repr(self.layer_name),'\n']
            init_code = exporter.create_init_code(*info)
            custom_code += [init_code]
            xIndent = _INDENT * 2
            name = 'self'
        else:
            name = storage_name
            if not dummy or dummy.image_file != self.image_file:
                custom_code += [baseIndent, name, '.', 'image = ', 
                                     repr(self.image_file),'\n']
            if not dummy or dummy.layer_name != self.layer_name:
                custom_code += [baseIndent, name, '.', 'layer = ', 
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
        if not custom_attr_code and storageDict['as_class']:
            custom_attr_code = [baseIndent, xIndent, 'pass\n']
        custom_code += custom_attr_code
        if not custom_code and storageDict['as_class']:
            custom_code = [baseIndent, 'pass\n']
        code += custom_code
        if DEBUG: print "*******************exit sprite save: "+str(self)        
        return ''.join(code)
    
    def _test_referrers(self):
        """_test_referrers
        
Just a debug test to make sure that pug doesn't keep the object alive when it's
supposed to be deleted.
"""
        import gc
        gc.collect()
        a = gc.get_referrers(self)   
        for ob in a:
            print ob
#            b = gc.get_referrers(ob)
#            for ob2 in b:
#                print "   ", ob2 
            print "_______________________"
        pass
    
    _codeStorageDict = {
            'skip_attributes': ['_actions', '_image_file', 'image_file', 
                                'layer_name','_init_image','_init_layer'], 
            'instance_attributes': ['*'],
            'instance_only_attributes':['gname'],
            'init_method':'on_create',
            'init_method_args': None,
            'force_init_def': True,
            'custom_export_func': _create_object_code,
            'as_class': True,
                        }
    add_subclass_skip_attributes(_codeStorageDict, pug.BaseObject)    

# force derived classes to use PugSprite as a base
#PugSprite._codeStorageDict['base_class'] = PugSprite

_spriteTemplate = {
    'name':'Editor',
    'attributes':
    [
        ['', pug.Label, {'label':'Sprite','font_size':10}],
        ['gname'],
        ['is_template', None, {'tooltip':
                '\n'.join(["Select this to automatically save this sprite",
                           "in the objects folder when the scene is saved.",
                           "It will not appear in the game."])}],
        ['layer_name', pug.Dropdown, {'list_generator':get_available_layers,}],
        ['save_sprite', None, {'label':'   Save Object',
                               'use_defaults': True}],
        ['', pug.Label, {'label':' Spacial'}],
        ['position'],
        ['rotation'],
        ['scale'],
        ['', pug.Label, {'label':' Image'}],
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
        ['', pug.Label, {'label':' Components'}],
        ['', pug.Components],
        ['', pug.Label, {'label':' Functions'}],
        ['delete'],
#        ['_delete_test'],
#        ['_test_referrers'],
    ]       
 }
pug.add_template('PugSprite', _spriteTemplate, True)