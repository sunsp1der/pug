### import autocode ###
from objects.RedDragon import RedDragon
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Midi_Input, Midi_To_Key,\
    Midi_Spawn, Spawn_Flower, Textbox, Key_Attribute, Midi_Dancer
### End import autocode ###

from objects.Grower import Grower

### MyScene autocode ###
class MyScene(PigScene):
    layers = ['Background', 'Sky']

    def on_enter(self):
        self.components.add( Utility_Keys() )
        self.components.add( Midi_Input(
                test_mode=True) )
        self.components.add( Midi_To_Key() )

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (207.0, 253.0)
        pigsprite_instance.components.add( Midi_Spawn(
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0.4,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )
        pigsprite_instance.components.add( Spawn_Flower() )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (358.0, 537.0)
        pigsprite_instance_2.components.add( Midi_Spawn(
                channel_range=(0, 1),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.image = 'art\\pug.png'
        pigsprite_instance_3.layer = 'Background'
        pigsprite_instance_3.position = (482.0, 534.0)
        pigsprite_instance_3.components.add( Midi_Spawn(
                channel_range=(1, 2),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        pigsprite_instance_4 = PigSprite()
        pigsprite_instance_4.image = 'art\\pug.png'
        pigsprite_instance_4.layer = 'Background'
        pigsprite_instance_4.position = (609.0, 530.0)
        pigsprite_instance_4.components.add( Midi_Spawn(
                channel_range=(2, 3),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        pigsprite_instance_5 = PigSprite()
        pigsprite_instance_5.image = 'art\\pug.png'
        pigsprite_instance_5.layer = 'Background'
        pigsprite_instance_5.position = (734.0, 528.0)
        pigsprite_instance_5.components.add( Midi_Spawn(
                channel_range=(3, 4),
                rapid_fire=False,
                spectrum_range=(48, 60),
                spawn_object='Petal',
                spawn_interval=0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0),
                match_scale=True) )

        pigsprite_instance_6 = PigSprite()
        pigsprite_instance_6.layer = 'Background'
        pigsprite_instance_6.position = (10.0, 515.0)
        pigsprite_instance_6.components.add( Textbox(
                text="This is a demo of Pig responding to midi input. If it doesn't work, check the console for info about midi data, then be sure the input_id is correct in the 'Midi_Input' Scene component.",
                font_size=14,
                max_width=250) )

        pigsprite_instance_7 = PigSprite()
        pigsprite_instance_7.image = 'art\\pug.png'
        pigsprite_instance_7.layer = 'Background'
        pigsprite_instance_7.position = (551.0, 120.0)
        pigsprite_instance_7.scale = (0.2, 0.2)
        pigsprite_instance_7.components.add( Key_Attribute(
                change_value=(1, 1)) )

        pigsprite_instance_8 = PigSprite()
        pigsprite_instance_8.layer = 'Background'
        pigsprite_instance_8.position = (341.0, 379.0)
        pigsprite_instance_8.components.add( Midi_Dancer(
                file='art\\dragon.png',
                grid_width=75,
                grid_height=70,
                end_frame=80) )

        reddragon_instance = RedDragon()
### End MyScene autocode ###

    def on_start(self):
        print "1"
        for x in range(0,801,80):
            for y in range(0,601,60):
                Grower_instance = Grower(gname='Grower')
                Grower_instance.position = (x, y)
        print "2"
