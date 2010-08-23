"Timer_Text.py"
from Opioid2D.public.Node import Node
from Opioid2D import Delay, CallFunc

from pug import Text
from pug.component import *

from pig.components.gui.Value_Tracker_Text import Value_Tracker_Text
from pig.components.gui.Textbox import Textbox
from pig.util import get_gamedata

class Timer_Text(Value_Tracker_Text):
    "Show and update gamedata.timer."
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['prefix',Text,{'doc':'Display this before the time'}],
            ['start_time',"Starting value of timer, in seconds"],
            ['end_time',"Ending value of timer, in seconds.\n"+\
                        "-1 means no end time."],
            ['show_minutes',"Display number of minutes elapsed,"+\
                            "instead of a large number of seconds."]
            ]
    _field_list += Textbox._font_fields    

    value_name = 'timer'
    start_time = 60
    end_time = 0
    _show_minutes = True
    _prefix = 'Time '
        
    interval = 0.5

    @component_method
    def on_added_to_scene(self, scene):
        """Set score to zero unless otherwise set"""
        self.start_time = float(self.start_time)
        Value_Tracker_Text.on_added_to_scene(self, scene, self.start_time)
        if self.end_time < self.start_time:
            self.interval = - abs(self.interval)
        if self.interval:
            self.timer_tick(0)
            
    @component_method
    def time_up(self):
        pass
        
    def timer_tick(self, amount=None):
        if amount == None:
            amount = self.interval 
        gamedata = get_gamedata()
        value = getattr(gamedata, "timer")
        setattr(gamedata, "timer", 
                getattr(gamedata, "timer") + amount)
        if self.end_time >=0:
            if self.interval < 0 and value <= self.end_time or\
                        self.interval > 0 and value >= self.end_time:
                self.time_up()
                return
        if self.interval:
            self.owner.do( Delay(abs(self.interval)) + \
                       CallFunc(self.timer_tick))
            
    @component_method
    def set_text(self, text=None):
        "Show current value"
        gamedata = get_gamedata()
        if text is None:
            val = getattr(gamedata, 'timer', None)
            if self.show_minutes:
                if val is None:
                    text = "00:00"
                else:
                    minutes = int(val / 60)
                    seconds = int(val % 60)
                    text = str(minutes) + ':' + str(seconds)
            else:
                if val is None:
                    text = "00"
                else:
                    text = "%0.f" % val
            text = self.prefix + text
        Textbox.set_text( self, text)
        
    def set_show_minutes(self, show_minutes):
        self._show_minutes = show_minutes
        self.set_text()
    def get_show_minutes(self):
        return self._show_minutes
    show_minutes = property(get_show_minutes, set_show_minutes)

register_component( Timer_Text)
