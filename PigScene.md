PigScene is the base scene object for the Pig system.

### Callbacks ###

A number of callbacks are received by PigScene. These are useful for responding to events as well as for stacking with Components:
```
def on_enter(self):
    "called when the scene is entered, whether in the editor or not"

def on_exit(self): 
    "called when the scene is exitted"

def on_project_start(self):
    "called when project is started with this scene"

def on_start(self):
    "called when the scene is started"
```