### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Mouse_Click_Destroy, Timer_Text
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.components.add( Mouse_Click_Destroy() )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (410.0, 310.0)
        pigsprite_instance_2.components.add( Mouse_Click_Destroy() )

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.layer = 'Background'
        pigsprite_instance_3.position = (577.0, 341.0)
        pigsprite_instance_3.tint = (0, 255, 0)
        pigsprite_instance_3.components.add( Mouse_Click_Destroy() )
        pigsprite_instance_3.components.add( Timer_Text(
                start_value=2.0) )
### End MyScene autocode ###
