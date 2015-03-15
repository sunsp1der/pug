## Pig's Action System ##

The Pig Editor allows you to layout your scene and, with the help of components, add quite a bit of functionality. Another way to add functionality to your objects is by using **Actions**. Many Actions have to do with object movement, but there are many kinds of Actions available.

## Getting Started Coding ##

To create the examples in this tutorial, we'll start with a new sprite in a new scene. To do this:
  1. Start the Pig Editor by running edit\_project.py
  1. Select New Scene in the _Scene_ dropdown in the Project tab.
  1. Select Save Scene and enter 'Tutorial' as the name.
  1. Select New Sprite in the _Object to add_ dropdown in the Project tab.
  1. Press the Add Object button. A new sprite will appear in the center of the Canvas.
  1. Click on the Save Object button on the _Selection: PigSprite_ tab
  1. Enter the name 'Tester' in the dialog
  1. In the Editor's View menu, select View Source

An editor window showing Tutorial.py will appear with the following code:
```
### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

### Tester autocode ###
class Tester(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 300.0)
### End Tester autocode ###
```

## Adding an Action and Testing ##

Let's add a basic Action to our pigsprite. To do this, first we need to import all the Actions into our file. Add this code after the _End import autocode_ line.
```
from pig.actions import *
```
This makes all the standard Actions available. You can also import them individually by replacing the '`*`' with their names, but for now we're just importing them all at once.

Next, add the following code after the _End Tester autocode_ line.
```
    def on_added_to_scene(self, scene):
        self.do( MoveDelta( (100,50), 1))
```
Your file should now look like this:
```
### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

from pig.actions import *

### Tester autocode ###
class Tester(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 300.0)
### End Tester autocode ###

    def on_added_to_scene(self, scene):
        self.do( MoveDelta( (100, 50), 1))
```
What we are doing here is creating an on\_added\_to\_scene method for our Tester object. This method will automatically be called when a Tester sprite is added to a scene. The arguments are _self_ and _scene_ which refer to the object itself and the scene it is being added to.
Next is the cool part: we tell the object (self) to _do_ an Action. The action is this:
```
    MoveDelta( (x, y), seconds))
```
MoveDelta is an action that basically says 'move this much'. So, this particular MoveDelta action moves the object 100 units right along the x-axis and 50 units down along the y-axis. It takes one second to do that.

## Testing ##

Don't believe me? Check it out...
  1. Save the Tester.py file in the code editor
  1. Press the Reload Files button on the Project tab of the Editor
  1. Press the Run button in the Controls row of the Project
You can use this same method for testing any of the Actions and Action chains in this tutorial. Don't forget to push the Stop button before you continue...

## Chaining Actions ##

You can perform one action after another simply by using the + sign when assigning actions to your sprite. For example, change the code in your on\_added\_scene method to look like this:
```
    def on_added_to_scene(self, scene):
        self.do( MoveDelta( (100, 50), 1) + MoveDelta( (-100, -50), 2))
```
When you try it, you'll see that your sprite now moves down and to the right, then back to its starting position (a little more slowly). Let's add one more Action to our chain, a Delete action. Change the method to look like this:
```
    def on_added_to_scene(self, scene):
        self.do( MoveDelta( (100, 50), 1) + MoveDelta( (-100, -50), 2) + \
                    Delete())
```
Note that the '\' at the end of the line just means that the code will continue on the next line. So now try that. Just what we expected... move, return, delete.

## Forking Actions ##
You can also make two Actions happen at the same time with a special Action called **Fork**. Inside a Fork action, you can write another Action chain that starts immediately. As an example, we'll use the RotateDelta action, which rotates a sprite and looks like this:
```
RotateDelta( degrees, seconds)
```
First, try it without the fork, like this:
```
    def on_added_to_scene(self, scene):
        self.do( MoveDelta( (100, 50), 1) + RotateDelta(180, 2) + \
                 MoveDelta( (-100, -50), 2) + Delete())
```
Try it. Just a regular chain. Move, rotate, move, then delete. Now we'll use a Fork with the RotateDelta. Change it to look like this:
```
    def on_added_to_scene(self, scene):
        self.do( MoveDelta( (100, 50), 1) + Fork( RotateDelta(180, 2)) + \
                 MoveDelta( (-100, -50), 2) + Delete())
```
Try it. Now it rotates at the same time as it moves back to its starting position. Basically, a Fork action just starts whatever Actions are inside it, then immediately goes on to the next Action in the original chain.
## More Action Tricks ##
There are lots of other Actions you can work with to achieve the results you're looking for. To see a full list, and more detailed documentation, check out [Actions](Wikipage.md).