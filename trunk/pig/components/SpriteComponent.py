from pug.component import *
from pig.PigDirector import PigDirector
 
class SpriteComponent( Component):
    """SpriteComponents call on_added_to_scene and on_first_display when added
to a running scene. This can be cancelled by setting the component's 
_auto_scene attribute to False"""
    _auto_scene = True
    def on_added_to_object( self):
        if self._auto_scene:
            scene = PigDirector.scene
            if scene.started and self.owner in scene.nodes:
                if hasattr(self,'on_added_to_scene'):
                    self.on_added_to_scene()
                if hasattr(self,'on_first_display'):
                    self.on_first_display()
                