from pug.component import * 

class XComponent(Component):
    _type = 'effect/special'
    _set = 'Testers'
    _attribute_list = [['defaultsize', 'The default size']]
    def __init__(self, **kwargs):
        self.defaultsize = 12
        Component.__init__(self, **kwargs)

    @component_method
    def explode(self, owner, size, i=2, *args):
        if size is None:
            size = self.defaultsize
        print "%s explosion %s" % (size, i)
        print self,owner
        
register_component(XComponent)

class X2Component(Component):
    _type = 'effect'
    _set = 'Testers'

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
    
    x2comp2 = X2Component()
    obj.components.add(x2comp2)
    print "--- obj.explode with XComponent AND X2Component"
    obj.explode("some other size", 20)
    print "----"

    obj.components.remove(xcomp)
    print "--- obj.explode with X2Component"
    obj.explode("some third size", 20)
    print
    print "STORAGE TEST"
    xcomp.defaultsize = 33
    print xcomp._create_object_code({'storage_name':'xcomp', 'as_class':0},0,0)
    print "----"

    print "Component delete when owner is deleted test..."
    obj2.components.add(XComponent)
    import weakref, gc
    compref = weakref.ref(obj2.components.get_one(XComponent))
    print "component: ",compref()
    del(obj2)
    print "might be None: ",compref()
    gc.collect()
    print "should be None: ", compref()
    if compref():
        func = compref().explode
        non_comp_func = compref()._set_owner
        g = gc.get_referrers(compref())   
        for ob in g:
            print ob
            b = gc.get_referrers(ob)
            for ob2 in b:
                print "   ", ob2 
            print "_______________________"     
    
    print "SHOULD FAIL"
    obj.components.remove(x2comp2)
    print "--- obj.explode with no components"
    obj.explode("not work", 20)
    print "----"    
    


