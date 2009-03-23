"""__Working__.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area, Forward_Motion, Life_Zone
from objects.PurpleFacer import PurpleFacer
from objects.UpFO import UpFO
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

##############################
# "AimedSpawn_Test" autocode #
##############################
class AimedSpawn_Test(PugScene):
    started = True
    layers = ['Background']
    def on_enter(self):
        # Sprites
        purplefacer_instance = PurpleFacer()
        purplefacer_instance.acceleration.x = -81.190536499023438
        purplefacer_instance.acceleration.y = -58.378902435302734
        purplefacer_instance.position.x = 373.50433349609375
        purplefacer_instance.position.y = 268.56304931640625
        purplefacer_instance.velocity.x = -40.595268249511719
        purplefacer_instance.velocity.y = -29.189451217651367
        purplefacer_instance.rotation = -54.282508850097656
        purplefacer_instance.components.add( Spawn_Area(
                object='UpFO',
                spawn_interval=0.29999999999999999,
                spawn_variance=0.0,
                spawn_location='center',
                spawn_offset=(1, 0)) )
        purplefacer_instance.components.add( Forward_Motion(
                velocity=50) )

        upfo_instance = UpFO()
        upfo_instance.position.x = 97.024505615234375
        upfo_instance.position.y = 8.1809778213500977
        upfo_instance.velocity.x = -405.95248413085937
        upfo_instance.velocity.y = -291.89480590820312
        upfo_instance.rotation = 305.717529296875
        upfo_instance.components.add( Life_Zone(
                x=-27.064737205448719,
                y=-27.064737205448719,
                width=None,
                height=None,
                xx=827.06473720544875,
                yy=627.06473720544875) )
        upfo_instance.components.remove_duplicate_of( Life_Zone() )

        upfo_instance_2 = UpFO()
        upfo_instance_2.position.x = 206.67422485351562
        upfo_instance_2.position.y = 87.022972106933594
        upfo_instance_2.velocity.x = -405.95248413085937
        upfo_instance_2.velocity.y = -291.89480590820312
        upfo_instance_2.rotation = 305.717529296875
        upfo_instance_2.components.add( Life_Zone(
                x=-27.064737205448719,
                y=-27.064737205448719,
                width=None,
                height=None,
                xx=827.06473720544875,
                yy=627.06473720544875) )
        upfo_instance_2.components.remove_duplicate_of( Life_Zone() )

        upfo_instance_3 = UpFO()
        upfo_instance_3.position.x = 311.23507690429687
        upfo_instance_3.position.y = 162.20584106445312
        upfo_instance_3.scale.x = 0.50199997425079346
        upfo_instance_3.scale.y = 0.50199997425079346
        upfo_instance_3.velocity.x = -405.95254516601562
        upfo_instance_3.velocity.y = -291.89471435546875
        upfo_instance_3.rotation = 305.71749877929687
        upfo_instance_3.components.add( Life_Zone(
                x=-27.064737205448719,
                y=-27.064737205448719,
                width=None,
                height=None,
                xx=827.06473720544875,
                yy=627.06473720544875) )
        upfo_instance_3.components.remove_duplicate_of( Life_Zone() )

##################################
# End "AimedSpawn_Test" autocode #
##################################

