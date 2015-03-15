PigSprite is the base sprite object for the Pig system.

### Callbacks ###

A number of callbacks are received by PigSprite. These are useful for responding to events as well as for stacking with Components:
```
def on_added_to_scene(self, scene):
    "called when first added to a scene"

def on_collision(self, toSprite, fromSprite, toGroup, fromGroup):
    """called when PigSprite collides with something. 
        
        toSprite: the sprite that collided (usually same as self)
        fromSprite: the sprite we collided with
        toGroup: toSprite's group that set off the collision
        fromGroup: fromSprite's group that set off the collision"""

def on_delete(self): 
    "called when PigSprite is actually being deleted."

def on_destroy(self): 
    "called when PigSprite's destroy method is called. Destroy is a special Pig feature that can be blocked by some effects (such as the Fade component)."

def on_first_display(self): 
    "called after on_added_to_scene but before PigSprite is displayed for the first time"

def on_project_start(self):
    "called when project is started"
```
## Mouse Callbacks ##
There are also a number of [mouse event callbacks](PigSprite_mouse_events.md) that you can register to receive.

## Built In Controls ##

A PigScene automatically has two keys registered: Ctrl-Q to quit and escape to pause.