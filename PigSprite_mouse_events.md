# Registering To Receive Mouse Callbacks #

To receive any of the callbacks below, you must register the sprite. To register, simply call PigSprite.mouse\_register(type). The argument type must contain "multi" (the default), "single", or "click".
  * "single": get all mouse events, and, if this sprite is the top gui sprite, don't let any other sprites get mouse events
  * "multi": get all mouse events and let other sprites get mouse events
  * "click": only get press, release, click, and drag events, and let other sprites get mouse events

# Callbacks #

The following mouse callbacks are available:
```
def on_enter(self):
    "The mouse has entered the sprite's area"
    
def on_exit(self):
    "The mouse has left the sprite's area"
    
def on_press(self):
    "The mouse button has been pressed in the sprite's area"
    
def on_release(self):
    "The mouse button has been released in the sprite's area"
    
def on_click(self):
    "The mouse button has been pressed AND released in the sprite's area"
        
def on_drag(self):
    "Called each frame while the sprite is being dragged"
    
def on_drag_begin(self):
    "The sprite is beginning to be dragged"
    
def on_drag_end(self):
    "The sprite has been released after dragging"
```