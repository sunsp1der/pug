from Opioid2D import Sprite, Director
from Opioid2D.public.Node import Node
from Opioid2D.public.Sprite import SpriteMeta

import pug
from pug.syswx.attributeguis import *
from pug.code_storage import add_subclass_skip_attributes
from pug.code_storage.constants import _INDENT
from pug_opioid.editor.util import get_available_layers, save_object

import sys
class PugSprite(Sprite, pug.BaseObject):
    """PugSprite( img=None, gname='')
    
Opioid2d Sprite with features for use with pug
"""
    __metaclass__ = SpriteMeta
    _pug_template_class = 'PugSprite'

    # image stuff... allows entry and storage of filename
    _image_file = None   
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
        Director.scene.update_node(self)
    gname = property( pug.BaseObject._get_gname, _set_gname, 
                      pug.BaseObject._del_gname,
                      "An easily accessed global name for this object")

    def _on_mgr_delete(self):
        Sprite._on_mgr_delete(self)        
        Director.scene.update_node(self) # register self with scene                

    # layer_name property
    def set_layer(self, layer):
        if layer not in Director.scene.layers:
            Director.scene.add_layer(layer)
        Sprite.set_layer(self, layer)
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
        if not base_code.endswith('pass\n'): # clean up pass case (for looks)
            code.append(base_code)
        # custom code
        baseIndent = _INDENT * indentLevel    
        hasAttrs = False    
        if storageDict['as_class']:
            code += [baseIndent, _INDENT, 'image = ', 
                     repr(self.image_file),'\n']
            code += [baseIndent, _INDENT, 'layer = ', 
                             repr(self.layer_name),'\n']
            init_code = exporter.create_init_code(*info)
            code += [init_code]
            xIndent = _INDENT * 2
            name = 'self'
        else:
            name = storage_name
            code += [baseIndent, name, '.', 'image = ', 
                                     repr(self.image_file),'\n']
            code += [baseIndent, name, '.', 'layer = ', 
                                     repr(self.layer_name),'\n']
            xIndent = ''
        vectorList = [('acceleration', (0, 0)),
                      ('position', (0, 0)),
                      ('scale', (1.0, 1.0)),
                      ('velocity', (0, 0))]
        prefix = ''.join([baseIndent, xIndent, name, '.'])
        for attr, default in vectorList:
            vector = getattr(self, attr)
            if (vector.x, vector.y) != default:
                code += [prefix, attr, '.', 'x = ', repr(vector.x),'\n']
                code += [prefix, attr, '.', 'y = ', repr(vector.y),'\n']
        
        # delete dummies from Opioid scene
        dummyList = storageDict['dummy_list']
        for item in dummyList:
            if isinstance(item, Node):
                item.delete()
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
            b = gc.get_referrers(ob)
            for ob2 in b:
                print "   ", ob2 
            print "_______________________"
        pass
    
    _codeStorageDict = {
            'skip_attributes': ['_actions', '_image_file', 'image_file', 
                                'layer_name','_init_image','_init_layer'], 
            'instance_attributes': ['*'],
            'init_method':'on_create',
#            'init_method_args': None, 
            'custom_export_func': _create_object_code,
            'as_class': True,
                        }
    add_subclass_skip_attributes(_codeStorageDict, pug.BaseObject)    

# force derived classes to use PugSprite as a base
PugSprite._codeStorageDict['base_class'] = PugSprite

_spriteTemplate = {
    'name':'Editor',
    'attributes':
    [
        ['', pug.Label, {'label':'Sprite','font_size':10}],
        ['gname'],
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