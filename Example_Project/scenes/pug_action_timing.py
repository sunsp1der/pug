from Opioid2D import *

from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite

class TestSprite(PugSprite):
    image = "art/sprite.png"
    layer = "sprite"
        
class TimingScene(PugScene):
    layers = ["sprite",'two']
    groups = ['group_a', 'grp_b']
    def enter(self):
        s = TestSprite()
        s.position = (200,100)
        s.do(
            MoveDelta((200,0), secs=4, mode=StopMode)
            )

        s = TestSprite()
        s.position = (200,200)
        s.do(
            MoveDelta((200,0), secs=4, mode=PingPongMode)
            )
        _s = TestSprite()
        _s.position = (200,300)
        _s.velocity = 50,0
        _s.do(
            Delay(4) + SetAttr(velocity=(0,0))
            )     