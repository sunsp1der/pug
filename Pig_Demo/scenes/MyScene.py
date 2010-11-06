### import autocode ###
from objects.dummy import dummy
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Key_Spawn, Set_Attribute, Key_Attribute,\
    Key_Component
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Archetypes
        dummy_archetype = dummy(gname='dummy')
        dummy_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (405.0, 458.0)
        pigsprite_instance.components.add( Key_Component(
                component_name='bloopy') )
        pigsprite_instance.components.add( Key_Spawn(
                gname='bloopy',
                spawn_object='dummy') )
        pigsprite_instance.components.add( Set_Attribute(
                attribute='tint',
                change_value=(255, 0, 255)) )
        pigsprite_instance.components.add( Key_Attribute() )
## End MyScene autocode ###