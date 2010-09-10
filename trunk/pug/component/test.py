import weakref, gc, sys, traceback
from pug.component import * 

class XComponent(Component):
    _type = 'effect/special'
    _set = 'Testers'
    _field_list = [['defaultsize', 'The default size']]
    defaultsize = 12

    @component_method
    def explode(self, size, i=2, *args):#, *args):
        print args
        if size is None:
            size = self.defaultsize
        print "%s explosion %s" % ( size, i)
        print self
        
    @component_method
    def fake(self):
        pass
        
register_component(XComponent)

class X2Component(Component):
    _type = 'effect'
    _set = 'Testers'

    @component_method
    def explode3(self, i=3, *a, **kw):#, size, i=3, **kw_args):
        print
        print a, kw        
        print x #@UndefinedVariable
        x = 15
        print "stuff", x
        print "%s explosion2 %s" % (size, i) #@UndefinedVariable

    @component_method
    def explode(self, size, i, *args):
        print "%s explosion2 %s" % (size, i)
        
    @component_method
    def explode2(self, r, *a):#, size, i=3, **kw_args):
        print
        print x #@UndefinedVariable
        x = 15
        print "stuff", x
        print "%s explosion2 %s" % (size, i) #@UndefinedVariable
        
register_component(X2Component)
        
if __name__ == "__main__":
    obj = ComponentObject() #@UndefinedVariable
    obj2 = ComponentObject() #@UndefinedVariable

    xcomp = XComponent()
    obj.components.add(xcomp)
    print "--- obj.explode(size='some size') with XComponent"
    obj.explode(size="some size")
    print "--- obj.explode(i=12) with XComponent... should exception"
    try:
        obj.explode(i=12)
    except:
        print traceback.format_exc()
    print
    
    x2comp2 = X2Component()
    obj.components.add(x2comp2)
    print "--- obj.explode with XComponent AND X2Component"
    obj.explode("some size", 3, 'and', 'much', more='more')
    print "----"
    print

    obj.components.remove(xcomp)
    print "--- obj.explode with X2Component"
    obj.explode("some third size", 20)
    print
    print "STORAGE TEST"
    xcomp.defaultsize = 33
    print xcomp._create_object_code({'storage_name':'xcomp', 'as_class':0},0,0)
    print "----"
    print
    
    print "Component delete when object is deleted test..."
    comp = XComponent()
    print "new component:", comp
    obj2.components.add(comp)
    compref = weakref.ref(comp)
    del(comp)
    print compref
    del(obj2)
    print "might be None: ",compref()
    gc.collect()
    print "should be None: ", compref()
    if compref():
        g = gc.get_referrers(compref())   
        for ob in g:
            print ob
            b = gc.get_referrers(ob)
            for ob2 in b:
                print "   ", ob2 
                c = gc.get_referrers(ob2)
            print "_______________________" 

    print
    print "Component delete when component is removed test..."
    comp = XComponent()
    print "new component:", comp
    obj.components.add(comp)
    obj.components.remove(comp)
    compref = weakref.ref(comp)
    del(comp)
    print "might be None: ",compref()
    gc.collect()
    print "should be None: ", compref()
    if compref():
        g = gc.get_referrers(compref())   
        for ob in g:
            print ob
            b = gc.get_referrers(ob)
            for ob2 in b:
                print "   ", ob2 
                c = gc.get_referrers(ob2)
            print "_______________________" 
                
    print
    
    print "SHOULD FAIL"
    obj.components.remove(x2comp2)
    print "--- obj.explode with no components"
    obj.explode("not work", 20)
    print "----"    
    
    
    


