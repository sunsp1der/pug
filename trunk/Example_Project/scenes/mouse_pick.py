from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite

class MousePick(PugScene):
    layers = [
        "foo",
        "bar",
        ]
    
    def enter(self):
        for x in range(10):
            s = PugSprite("art/sprite.png")
            s.set(
                layer = "foo",
                position = (x*50+100,x*50+50),
                )
            s.join_group("test")
        for x in range(10):
            s = PugSprite("art/sprite.png")
            s.set(
                layer = "bar",
                position = (x*50+200,x*50+50),
                )

    def handle_mousebuttondown(self, ev):
        x,y = ev.pos
        s = self.get_layer("bar").pick(x,y)
        if s is not None:
            s.scale *= 1.2
        s = self.get_layer("foo").pick(x,y)
        if s is not None:
            s.scale *= 0.8

#Display.init((800,600), title="Opioid2D Sprite Picking Test")
#Director.run(TestScene)
