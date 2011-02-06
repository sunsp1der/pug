### import autocode ###
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Utility_Keys, Midi_Input, Midi_To_Key,\
    Midi_Spawn, Spawn_Flower, Textbox, Key_Attribute_Change
### End import autocode ###

### Midi_Demo autocode ###
class Midi_Demo(Scene):
    def on_enter(self):
        self.components.add( Utility_Keys() )
        self.components.add( Midi_Input(
                                        test_mode=True) )
        self.components.add( Midi_To_Key() )

        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/pug.png'
        sprite_instance.layer = 'Background'
        sprite_instance.position = (207.0, 253.0)
        sprite_instance.components.add( Midi_Spawn(
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0.4,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )
        sprite_instance.components.add( Spawn_Flower() )

        sprite_instance_2 = Sprite()
        sprite_instance_2.image = 'art/pug.png'
        sprite_instance_2.layer = 'Background'
        sprite_instance_2.position = (358.0, 537.0)
        sprite_instance_2.components.add( Midi_Spawn(
                channel_range=(0, 1),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        sprite_instance_3 = Sprite()
        sprite_instance_3.image = 'art/pug.png'
        sprite_instance_3.layer = 'Background'
        sprite_instance_3.position = (482.0, 534.0)
        sprite_instance_3.components.add( Midi_Spawn(
                channel_range=(1, 2),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        sprite_instance_4 = Sprite()
        sprite_instance_4.image = 'art/pug.png'
        sprite_instance_4.layer = 'Background'
        sprite_instance_4.position = (609.0, 530.0)
        sprite_instance_4.components.add( Midi_Spawn(
                channel_range=(2, 3),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        sprite_instance_5 = Sprite()
        sprite_instance_5.image = 'art/pug.png'
        sprite_instance_5.layer = 'Background'
        sprite_instance_5.position = (734.0, 528.0)
        sprite_instance_5.components.add( Midi_Spawn(
                channel_range=(3, 4),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        sprite_instance_6 = Sprite()
        sprite_instance_6.layer = 'Background'
        sprite_instance_6.position = (10.0, 515.0)
        sprite_instance_6.components.add( Textbox(
                text="This is a demo of Pig responding to midi input. If it doesn't work, check the console for info about midi data, then be sure the input_id is correct in the 'Midi_Input' Scene component.",
                font_size=14,
                max_width=250) )

        sprite_instance_7 = Sprite()
        sprite_instance_7.image = 'art/pug.png'
        sprite_instance_7.layer = 'Background'
        sprite_instance_7.position = (551.0, 120.0)
        sprite_instance_7.scale = (0.2, 0.2)
        sprite_instance_7.components.add( Key_Attribute_Change(
                change_value=(1, 1)) )
### End Midi_Demo autocode ###
