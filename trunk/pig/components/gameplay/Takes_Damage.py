from Opioid2D import Delay, CallFunc
from Opioid2D.public.Node import Node

from pug.component import *
from pug import ColorPicker

from pig.components.collision.Join_Collision_Group import Join_Collision_Group
from pig.util import get_gamedata

class Takes_Damage(Join_Collision_Group):
    """Set this object to take damage from objects with Deals_Damage that
collide with it. 
This component gives the base object new callbacks:
    on_take_damage( amount, damager, health): called before object dies
    on_zero_health( amount, damager, health): called if health<=0, after 
auto_destroy
"""
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['start_health', 'The amount of health the object has'],
            ['auto_destroy', 'Destroy this object when health <= 0'],
            ['do_damage_tint', "Tint object as it's damaged"],
            ['damage_tint', ColorPicker, 
                                    {'doc':"Tint this object towards this\n"+
                                     "color as it's damaged"}],
            ['invincible_time', "After spawning, this object will not\n"+\
                                "be damaged for this many seconds"],
            ['value_name', 
                    'If this is not blank, current health\n'+\
                    'will be stored in gamedata.<value_name>']                                
            ]
    _field_list += Join_Collision_Group._field_list
    #defaults
    start_health = 100.0
    auto_destroy = True
    do_damage_tint = True
    damage_tint = ( 255, 0, 0)  
    invincible_time = 1
    value_name = ''
    
    _health = None
    invincible = True
      
    @component_method
    def on_first_display(self):
        """Set up health and collisions"""
        if self.health is None:
            self.health = float(self.start_health)
        self.start_tint = self.owner.tint
        self.tint_difference = (self.damage_tint[0]-self.start_tint[0],
                                self.damage_tint[1]-self.start_tint[1],
                                self.damage_tint[2]-self.start_tint[2],
                                )
        (Delay(self.invincible_time) + \
                CallFunc(self.set_invincible, False)).do()
            
    def set_invincible(self, val):
        self.invincible = val
        
    @component_method
    def take_damage(self, amount, damager=None):
        "take_damage( amount, damager=None): lose 'amount' of health"
        if self.invincible:
            return
        self.health -= amount
        try:
            self.owner.on_take_damage( amount, damager, self.health)
        except AttributeError:
            pass
        if self.health <= 0:
            if self.auto_destroy:
                self.owner.destroy()
            try:
                self.owner.on_zero_health( amount, damager, self.health)
            except AttributeError:
                pass
        if self.do_damage_tint:
            health = max(0, self.health)
            tint_amount = 1 - health/self.start_health # tint amount
            self.owner.tint = (
                    self.start_tint[0] + self.tint_difference[0] * tint_amount,
                    self.start_tint[1] + self.tint_difference[1] * tint_amount,
                    self.start_tint[2] + self.tint_difference[2] * tint_amount
                    )
            
    #making these component methods, gives you access at the base object level
    @component_method
    def set_health(self, health):
        "set_health(health): set self._health"
        self._health = health
        if self.value_name:
            gamedata = get_gamedata()
            setattr(gamedata, self.value_name, health)                    
    @component_method
    def get_health(self):
        "get_health()->self._health"
        return self._health
    health = property(get_health, set_health, doc = "Current health") 

register_component( Takes_Damage)
