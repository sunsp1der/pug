"""Load all components"""

from pig.components.SpriteComponent import SpriteComponent
from pig.components.behavior.Animate_Folder import Animate_Folder
from pig.components.behavior.Animate_Grid import Animate_Grid
from pig.components.behavior.Fade import Fade
from pig.components.behavior.Grow_Shrink import Grow_Shrink
from pig.components.behavior.Face_Object import Face_Object
from pig.components.behavior.Life_Zone import Life_Zone
from pig.components.behavior.Motion_Zone import Motion_Zone
from pig.components.behavior.Self_Destruct import Self_Destruct
from pig.components.behavior.Face_Motion import Face_Motion
from pig.components.behavior.Set_Motion import Set_Motion
from pig.components.behavior.Forward_Motion import Forward_Motion
from pig.components.behavior.Random_Motion import Random_Motion
from pig.components.behavior.Stop_Motion_On_Destroy \
                            import Stop_Motion_On_Destroy
from pig.components.behavior.Set_Attribute import Set_Attribute                            
from pig.components.collision.Collision_Callback import Collision_Callback
from pig.components.collision.Join_Collision_Group import Join_Collision_Group 
from pig.components.collision.Collision_Destroy import Collision_Destroy
from pig.components.collision.Stop_Wall import Stop_Wall 
from pig.components.controls.Mouse_Follow import Mouse_Follow
from pig.components.controls.Mouse_Face import Mouse_Face
from pig.components.controls.Mouse_Click_Destroy import Mouse_Click_Destroy
from pig.components.controls.Midi_Spawn import Midi_Spawn
from pig.components.controls.Key_Destroy import Key_Destroy
from pig.components.controls.Key_Attribute_Change import Key_Attribute_Change
from pig.components.controls.Key_Component_Change import Key_Component_Change
from pig.components.controls.Key_Direction_Controls \
                            import Key_Direction_Controls
from pig.components.controls.Key_Animate_Direction import Key_Animate_Direction
from pig.components.controls.Key_Drive_Controls import Key_Drive_Controls
from pig.components.gui.Scene_Button import Scene_Button
from pig.components.gui.Textbox import Textbox
from pig.components.gui.Value_Tracker_Text import Value_Tracker_Text
from pig.components.gui.Timer_Text import Timer_Text

from pig.components.gameplay.Value_On_Destroy import Value_On_Destroy
from pig.components.gameplay.Takes_Damage import Takes_Damage
from pig.components.gameplay.Deals_Damage import Deals_Damage
from pig.components.gameplay.Multiple_Lives import Multiple_Lives
from pig.components.spawn.Spawner import Spawner
from pig.components.spawn.Spawn_On_Destroy import Spawn_On_Destroy

from pig.components.spawn.Spawn_Flower import Spawn_Flower
from pig.components.spawn.Spawned_Attribute_Change import Spawned_Attribute_Change
from pig.components.spawn.Spawned_Component_Change import Spawned_Component_Change
from pig.components.spawn.Key_Spawn import Key_Spawn
from pig.components.sound.On_Create_Sound import On_Create_Sound
from pig.components.sound.On_Destroy_Sound import On_Destroy_Sound
from pig.components.sound.On_Deal_Damage_Sound import On_Deal_Damage_Sound
from pig.components.sound.On_Take_Damage_Sound import On_Take_Damage_Sound
from pig.components.sound.Key_Sound import Key_Sound
from pig.components.sound.On_Collision_Sound import On_Collision_Sound
from pig.components.scene.Midi_To_Key import Midi_To_Key
from pig.components.scene.Utility_Keys import Utility_Keys
from pig.components.scene.On_Start_Sound import On_Start_Sound
from pig.components.scene.Scene_Timer import Scene_Timer
from pig.components.scene.Midi_Input import Midi_Input
from pig.components.scene.Joystick_Input import Joystick_Input
from pig.components.scene.Joystick_Axis_To_Key import Joystick_Axis_To_Key
from pig.components.scene.Joystick_Button_To_Key import Joystick_Button_To_Key
from pig.components.scene.Key_Sound_Scene import Key_Sound_Scene
