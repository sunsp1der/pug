from pug.component import *

from pig.components.collision.Collision_Callback import Collision_Callback

class Collision_Destroy( Collision_Callback):
    
    @component_method
    def on_collision(self, toSprite, fromSprite, toGroup, fromGroup):
        self.owner.destroy()
        
register_component( Collision_Destroy)