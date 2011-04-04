"""ScenesDropdown attribute gui"""
import wx

from Opioid2D import Scene as OpioidScene

from pug.util import sort_case_insensitive
from pug.syswx.attributeguis.dropdown import Dropdown

from pig.util import get_available_scenes

class ScenesDropdown (Dropdown):
    """PIG scene selection attribute GUI
    
ScenesDropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'class_list': a list of acceptable object classes. If this is empty or 
        non-existent, all Opioid2D.Node objects will be listed as options.
    'append_list': a list of ("name",obj) options to add to end of list.
    'prepend_list': a list of ("name",obj) options to add to start of list.
    'none_choice': if value is -1, adds 'append_list':[('#None#',None)],
        otherwise if value evaluates to True, 'prepend_list':[('#None#',None)]
    'component': if True, sets 'none_choice':True and returns strings or None
        rather than actual classes. Used for component fields
    'show_hidden': if True, show scenes that start with "__". default False
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""      
    return_strings = False
    do_change = False
    def setup(self, attribute, window, aguidata):    
        specialaguidata = {'class_list': [OpioidScene],
                           'append_list':[],
                           'prepend_list':[],
                           'doc': 'Saved object class', 
                            'list_generator': self.scene_list_generator,
                            'show_hidden': False}
        specialaguidata.update(aguidata)
        if specialaguidata.get('component'):
            specialaguidata.setdefault('none_choice', True)
            self.return_strings = True
        none_choice = specialaguidata.get('none_choice')
        if none_choice == -1:
            specialaguidata['append_list'].append(('#None#',None))
        elif none_choice:
            specialaguidata['prepend_list'].insert(0,('#None#',None))
        specialaguidata['prepend_list'].reverse()
        self.class_list = aguidata.get('class_list',[])
        Dropdown.setup(self, attribute, window, specialaguidata)

    def set_control_value(self, value):
        # use name of value if we can
        if not value:
            self.control.SetText("")
            self.data = None
            return
        try:
            scenename = value.__name__
        except:
            scenename = value
        i = self.listctrl.FindText( scenename)
        if i != -1:
            self.listctrl.SelectItem(i)
            self.control.SetText( self.listctrl.GetStringValue())
            self.data = value
            self.set_tooltip()
        else:
            Dropdown.set_control_value(self, value)
            
    def apply(self, event=None):
        # only apply when user changes dropdown
        if not self.do_change:
            return
        Dropdown.apply(self, event)
        
    def item_selected(self, event=None):
        self.do_change = True
        Dropdown.item_selected(self, event)
        self.do_change = False

    def scene_list_generator(self):
        scenedict = get_available_scenes( 
                useWorking = wx.GetApp().projectObject._use_working_scene)
        if not self.aguidata['show_hidden']:
            for item in scenedict.keys():
                if item.startswith("__"):
                    scenedict.pop(item)
        if self.return_strings:
            scenelist = scenedict.keys()
        else:
            scenelist = [(name, scenedict[name]) for name in scenedict.keys()]
        sort_case_insensitive(scenelist)
        for item in self.aguidata['prepend_list']:
            scenelist.insert(0, item)
        for item in self.aguidata['append_list']:
            scenelist.append(item)
        return scenelist    

                        