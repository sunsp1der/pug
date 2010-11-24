### import autocode ###
from objects.dummy import dummy
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Textbox, Set_Component_Attribute,\
    Key_Component_Change, Spawner, Spawned_Component_Change,\
    Key_Attribute_Change, Spawned_Attribute_Change, Set_Attribute
### End import autocode ###

from objects.Grower import Grower

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (277.0, 429.0)
        pigsprite_instance.components.add( Textbox(
                gname='text',
                hotspot=(0, 5),
                enabled=False) )
        pigsprite_instance.components.add( Set_Component_Attribute(
                component_name='text',
                attribute='text',
                change_value='False') )
        pigsprite_instance.components.add( Key_Component_Change(
                key='A',
                component_name='text',
                attribute='font_size',
                change_value=50) )
        pigsprite_instance.components.add( Spawner(
                gname='text',
                spawn_object='dummy') )
        pigsprite_instance.components.add( Spawned_Component_Change(
                spawner_name='text',
                component_name='text',
                attribute='text',
                change_value='yup') )
        pigsprite_instance.components.add( Key_Attribute_Change(
                key='C',
                attribute='tint',
                change_value=(100, 100, 100)) )
        pigsprite_instance.components.add( Spawned_Attribute_Change() )
        pigsprite_instance.components.add( Set_Attribute(
                attribute='tint',
                change_value=(255, 0, 0)) )

        dummy_instance = dummy()
### End MyScene autocode ###

#
#    def on_start(self):
#        print "1"
#        for x in range(0,801,80):
#            for y in range(0,601,60):
#                Grower_instance = Grower(gname='Grower')
#                Grower_instance.position = (x, y)
#        print "2"
