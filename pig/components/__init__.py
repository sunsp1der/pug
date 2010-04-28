"""Load all components"""

from pig.components.behavior.Face_Object import Face_Object
from pig.components.behavior.Life_Zone import Life_Zone
from pig.components.behavior.Motion_Zone import Motion_Zone
from pig.components.behavior.Self_Destruct import Self_Destruct
from pig.components.behavior.Face_Motion import Face_Motion
from pig.components.behavior.Set_Motion import Set_Motion
from pig.components.behavior.Forward_Motion import Forward_Motion
from pig.components.behavior.Random_Motion import Random_Motion
from pig.components.behavior.Stop_Motion_On_Destroy import Stop_Motion_On_Destroy
from pig.components.collision.Collision_Callback import Collision_Callback
from pig.components.collision.Join_Group import Join_Group 
from pig.components.collision.Collision_Destroy import Collision_Destroy
from pig.components.controls.Mouse_Follow import Mouse_Follow
from pig.components.controls.Mouse_Face import Mouse_Face
from pig.components.controls.Key_Spawn import Key_Spawn
from pig.components.controls.Key_Direction_Controls \
                            import Key_Direction_Controls
from pig.components.controls.Key_Drive_Controls import Key_Drive_Controls
from pig.components.effects.Fade import Fade
from pig.components.effects.Grow_Shrink import Grow_Shrink
from pig.components.settings.Set_Gname import Set_Gname
from pig.components.spawn.Spawner import Spawner
from pig.components.spawn.Spawn_On_Destroy import Spawn_On_Destroy
from pig.components.sound.On_Destroy_Sound import On_Destroy_Sound
from pig.components.sound.On_Key_Sound import On_Key_Sound
from pig.components.sound.On_Collision_Sound import On_Collision_Sound
from pig.components.scene.Utility_Keys import Utility_Keys
from pig.components.scene.On_Start_Sound import On_Start_Sound
from pig.components.scene.Open_File_On_Start import Open_File_On_Start
