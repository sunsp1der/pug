### import autocode ###
from objects.Bullet import Bullet
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Key_Drive_Controls, Key_Spawn,\
    Collision_Destroy, Join_Group
### End import autocode ###

### ShootingGallery autocode ###
class ShootingGallery(PigScene):
    def on_enter(self):
        # Archetypes
        Bullet_archetype = Bullet(gname='Bullet')
        Bullet_archetype.archetype = True

        # Sprites
        cannon = PigSprite(gname='cannon')
        cannon.image = 'art\\pig.png'
        cannon.layer = 'Background'
        cannon.position.x = 418.0
        cannon.position.y = 514.0
        cannon.components.add( Key_Drive_Controls(
                forward_key=None,
                backward_key=None) )
        cannon.components.add( Key_Spawn(
                object='Bullet',
                spawn_location='center',
                spawn_offset=(0, -1),
                max_spawns_in_scene=1) )

        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pig.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 150.0
        pigsprite_instance.position.y = 153.0
        pigsprite_instance.scale.x = 0.5
        pigsprite_instance.scale.y = 0.5
        pigsprite_instance.color = (1.0, 0.0, 1.0, 1.0)
        pigsprite_instance.components.add( Collision_Destroy(
                with_group='bullet',
                my_group='target') )
        pigsprite_instance.components.add( Join_Group(
                group='target') )
### End ShootingGallery autocode ###
