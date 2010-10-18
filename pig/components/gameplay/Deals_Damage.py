from Opioid2D.public.Node import Node

from pug.component import *

from pig.components.collision.Collision_Callback import Collision_Callback

class Deals_Damage(Collision_Callback):
    """Set this object to deal damage to objects that collide with it, if those
objects have the Takes_Damage component.

This component gives the its owner a new callback:
    on_deal_damage( target, damage_amount): called before damage is dealt. If 
this returns a value, that value becomes the new damage_amount.
"""
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['damage_amount', 'damage_amount of damage this object deals'],
            ['destroy_on_damage', 'Destroy this object when it deals damage'],
            ['destroy_on_collide', 'Destroy this object when it collides'],
            ]
    _field_list += Collision_Callback._collision_list
    #defaults
    damage_amount = 100.0
    destroy_on_damage = True
    destroy_on_collide = False
                  
    @component_method
    def deal_damage(self, target, damage_amount=None):
        """deal_damage(target, damage_amount=self.damage_amount)->damage dealt

Deal 'damage_amount' of damage to target if that target has 'take_damage' 
method. If 'damage_amount' is None, use self.damage_amount.
"""
        if not callable(getattr(target, "take_damage", None)):
            # target doesn't take damage
            return None
        if damage_amount is None:
            damage_amount = self.damage_amount
        try:
            val = self.owner.on_deal_damage( target, damage_amount)
            if val is not None:
                damage_amount = val
        except AttributeError:
            pass
        if damage_amount:
            target.take_damage( damage_amount, self.owner)
            if self.destroy_on_damage:
                self.owner.destroy()
        return damage_amount
               
    @component_method        
    def on_collision(self, toSprite, fromSprite, toGroup, fromGroup):
        "When object collides, call deal_damage"
        self.deal_damage( fromSprite)

register_component( Deals_Damage)
