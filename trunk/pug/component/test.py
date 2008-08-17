from pug.component import * 

class XComponent(Component):
    _Type = 'effect/special'
    _Set = 'Testers'
    def __init__(self):
        self.defaultsize = 12

    @component_method
    def explode(self, owner, size, i=2, *args):
        if size is None:
            size = self.defaultsize
        print "%s explosion %s" % (size, i)
        print self,owner
        
register_component(XComponent)

class X2Component(Component):
    _Type = 'effect'
    _Set = 'Testers'

    @component_method
    def explode(self, owner, size, i=3, **kw_args):
        print "stuff"
        print "%s explosion2 %s" % (size, i)
        
register_component(X2Component)
        
if __name__ == "__main__":
    obj = ComponentObject()
    obj2 = ComponentObject()

    xcomp = XComponent()
    obj.components.add(xcomp)
    print "--- obj.explode with XComponent"
    obj.explode("some size", 3)

    #x2comp = X2Component()
    #obj2.add_component(x2comp)
    #print "--- obj2.explode with X2Component"
    #obj2.explode()
    
    x2comp2 = X2Component()
    obj.components.add(x2comp2)
    print "--- obj.explode with XComponent AND X2Component"
    obj.explode("some other size", 20)
    print "----"

    obj.components.remove(xcomp)
    print "--- obj.explode with X2Component"
    obj.explode("some third size", 20)
    print "----"
    obj.components.remove(x2comp2)
    print "--- obj.explode with no components"
    obj.explode("some not work size", 20)
    print "----"

