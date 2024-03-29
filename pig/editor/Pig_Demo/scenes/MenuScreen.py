### import autocode ###
from objects.Petal import Petal
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Utility_Keys, Scene_Button, Textbox, Spawner,\
    Spawn_Flower
### End import autocode ###

### MenuScreen autocode ###
class MenuScreen(Scene):
    layers = ['Background', 'text']

    def on_enter(self):
        self.components.add( Utility_Keys() )

        # Archetypes
        Petal_archetype = Petal(gname='Petal')
        Petal_archetype.archetype = True

        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/block.png'
        sprite_instance.layer = 'Background'
        sprite_instance.position = (397.0, 518.0)
        sprite_instance.scale = (100.0, 20.0)
        sprite_instance.components.add( Scene_Button(
                target='Dragon',
                hover_sound='sound/beep.wav',
                click_sound='sound/explosion.wav') )

        sprite_instance_2 = Sprite()
        sprite_instance_2.image = 'art/block.png'
        sprite_instance_2.layer = 'Background'
        sprite_instance_2.position = (659.0, 518.0)
        sprite_instance_2.scale = (100.0, 20.0)
        sprite_instance_2.components.add( Scene_Button(
                target='Shooting_Gallery',
                hover_sound='sound/beep.wav',
                click_sound='sound/explosion.wav') )

        sprite_instance_3 = Sprite()
        sprite_instance_3.image = 'art/block.png'
        sprite_instance_3.layer = 'Background'
        sprite_instance_3.position = (138.0, 518.0)
        sprite_instance_3.scale = (100.0, 20.0)
        sprite_instance_3.components.add( Scene_Button(
                target='Fly_Around',
                hover_sound='sound/beep.wav',
                click_sound='sound/explosion.wav') )

        sprite_instance_4 = Sprite()
        sprite_instance_4.layer = 'Background'
        sprite_instance_4.position = (181.0, 297.0)
        sprite_instance_4.components.add( Textbox(
                text='Python Inventor Gizmo',
                font_size=60) )

        sprite_instance_5 = Sprite()
        sprite_instance_5.layer = 'Background'
        sprite_instance_5.position = (341.0, 363.0)
        sprite_instance_5.components.add( Textbox(
                text='Demo',
                font_size=60) )

        sprite_instance_6 = Sprite()
        sprite_instance_6.image = 'art/pug.png'
        sprite_instance_6.layer = 'Background'
        sprite_instance_6.position = (401.0, 255.0)
        sprite_instance_6.components.add( Spawner(
                spawn_object='Petal',
                spawn_interval=0.3,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0)) )
        sprite_instance_6.components.add( Spawn_Flower(
                petals=3,
                rotation_range=150) )

        sprite_instance_7 = Sprite()
        sprite_instance_7.layer = 'text'
        sprite_instance_7.position = (580.0, 497.0)
        sprite_instance_7.tint = (0, 0, 0)
        sprite_instance_7.components.add( Textbox(
                text='Shooting Gallery') )

        sprite_instance_8 = Sprite()
        sprite_instance_8.layer = 'text'
        sprite_instance_8.position = (85.0, 497.0)
        sprite_instance_8.tint = (0, 0, 0)
        sprite_instance_8.components.add( Textbox(
                text='Fly Around') )

        sprite_instance_9 = Sprite()
        sprite_instance_9.layer = 'text'
        sprite_instance_9.position = (360.0, 497.0)
        sprite_instance_9.tint = (0, 0, 0)
        sprite_instance_9.components.add( Textbox(
                text='Dragon') )
### End MenuScreen autocode ###
