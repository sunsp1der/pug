import pug.all_components
from pug.component import Component

def get_all_components():
    list = dir(pug.all_components)
    clist = []
    for item in list:
        cls = getattr(pug.all_components, item)
        try:
            if issubclass(cls, Component):
                clist.append(cls)
        except:
            pass
    return clist