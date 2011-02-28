### import autocode ###
from objects.LetterPetal import LetterPetal
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Set_Mouse_Cursor, Key_Spawn, Spawn_Flower,\
    Spawned_Component_Change
### End import autocode ###

from pygame.key import name as key_name
from pig.keyboard import keymods
from pug import get_gnamed_object

### Flower autocode ###
class Flower(Scene):
    def on_enter(self):
        self.components.add( Set_Mouse_Cursor(
                image='art/pug.png') )

        # Archetypes
        LetterPetal_archetype = LetterPetal(gname='LetterPetal')
        LetterPetal_archetype.archetype = True

        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/pug.png'
        sprite_instance.layer = 'Background'
        sprite_instance.position = (400.0, 300.0)
        sprite_instance.alpha = 0.0
        sprite_instance.components.add( Key_Spawn(
                gname='spawner',
                spawn_object='LetterPetal',
                spawn_interval=0.2) )
        sprite_instance.components.add( Spawn_Flower(
                gname='flower') )
        sprite_instance.components.add( Spawned_Component_Change(
                gname='key_shifter',
                component_name='symbol',
                attribute='text',
                change_value='$') )
### End Flower autocode ###

        self.key_shifter = get_gnamed_object('key_shifter')
        self.spawner = get_gnamed_object('spawner')
        self.flower = get_gnamed_object('flower')
        
    def handle_keydown(self, event):
        key = str(event.unicode)
        if len(key) == 1:
            if key == "-":
                n = self.flower.petals - 1
                if n > 0:
                    self.flower.petals = n
            elif key == "=":
                n = self.flower.petals + 1
                self.flower.petals = n
            else:
                self.key_shifter.change_value = key 
                self.spawner.on_destroy() # unregister keys
                #  we know the key, so figure out shift
                if event.mod & 3:
                    mod = keymods["SHIFT"]
                else:
                    mod = 0
                self.spawner.key = (mod, event.key)
                self.spawner.k_info.append(
                        self.register_key_down( self.spawner.key, 
                                                 self.spawner.check_spawn))
                self.spawner.k_info.append(
                        self.register_key_up( event.key, 
                                               self.spawner.stop_spawning))
                self.spawner.k_info.append(
                        self.register_key_up( self.spawner.key, 
                                               self.spawner.stop_spawning))
                Scene.handle_keydown( self, event)
