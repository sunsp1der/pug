"""Load all components"""

from pig.components.behavior.Face_Object import Face_Object
from pig.components.behavior.Life_Zone import Life_Zone
from pig.components.behavior.Self_Destruct import Self_Destruct
from pig.components.behavior.Face_Motion import Face_Motion
from pig.components.collision.Collision_Callback import Collision_Callback
from pig.components.collision.Join_Group import Join_Group 
from pig.components.collision.Collision_Destroy import Collision_Destroy
from pig.components.controls.Follow_Mouse import Follow_Mouse
from pig.components.controls.Face_Mouse import Face_Mouse
from pig.components.controls.Keyboard_Direction_Controls \
                            import Keyboard_Direction_Controls
from pig.components.controls.Keyboard_Drive_Controls \
                            import Keyboard_Drive_Controls
from pig.components.effects.Fade import Fade
from pig.components.effects.Grow_Shrink import Grow_Shrink
from pig.components.physics.Set_Motion import Set_Motion
from pig.components.physics.Forward_Motion import Forward_Motion
from pig.components.physics.Random_Motion import Random_Motion
from pig.components.settings.Set_Gname import Set_Gname
from pig.components.spawn.Spawn_Area import Spawn_Area
from pig.components.spawn.Spawn_On_Destroy import Spawn_On_Destroy