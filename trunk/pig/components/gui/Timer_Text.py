"Timer_Text.py"
from Opioid2D.public.Node import Node
from Opioid2D import Delay, CallFunc

from pug import Text
from pug.component import *

from pig.components.gui.Value_Tracker_Text import Value_Tracker_Text
from pig.components.gui.Textbox import Textbox
from pig.util import get_gamedata

class Timer_Text(Value_Tracker_Text):
    """Show and update gamedata.timer. When time is up, owner's on_time_up 
method will be called."""
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['prefix',Text,{'doc':'Display this before the time'}],
            ['start_value',"Starting value of timer, in seconds"],
            ['end_value',"Ending value of timer, in seconds.\n"+\
                        "-1 means no end time."],
            ['gameover',"Call gamedata.gameover() when time is up"],
            ['show_minutes',"Display minutes:seconds on timer,\n"+\
                            "instead of a large number of seconds."],
            ]
    _field_list += Textbox._font_fields    

    value_name = 'timer'
    start_value = 60.0
    end_value = 0
    gameover = True
    _show_minutes = False
    _prefix = 'Time: '
        
    interval = 0.5
    
    @component_method
    def on_added_to_scene(self):
        """Set starting value"""
        gamedata = get_gamedata()
        try:
            getattr(gamedata, self.value_name)
        except:
            setattr( gamedata, self.value_name, float(self.start_value))
        Value_Tracker_Text.on_added_to_scene(self)
        if self.end_value < self.start_value:
            self.interval = - abs(self.interval)
        if self.interval:
            ( Delay(0) + CallFunc(self.timer_tick, 0)).do()       
            
    @component_method
    def on_time_up(self):
        """Callback for when timer reaches end_value"""
        if self.gameover:
            gamedata = get_gamedata()
            gamedata.gameover()
            
    def timer_tick(self, amount=None):
        if amount == None:
            amount = self.interval 
        gamedata = get_gamedata()
        value = gamedata.timer                
        newval = value + amount
        if self.end_value >=0:
            if self.interval < 0 and newval <= self.end_value or\
                        self.interval > 0 and newval >= self.end_value:
                gamedata.timer = self.end_value
                self.owner.do( Delay(0) + CallFunc(self.owner.on_time_up))
                return
        gamedata.timer = newval
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
