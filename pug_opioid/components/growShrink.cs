//-----------------------------------------------------------------------------
// GrowShrink.cs
//
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(GrowShrinkBehavior))
{
   GrowShrinkBehavior.delete();
}

%template = new BehaviorTemplate(GrowShrinkBehavior);
%template.friendlyName = "GrowShrink";
%template.behaviorType = "Effect";
%template.description  = "Grow this object in when spawned and/or shrink it out when deleted";

%template.addBehaviorField(growInTime, "Number of seconds to grow in the object when it's added to scene. Use zero for no grow in.", float, 2.0);      
%template.addBehaviorField(shrinkOutTime, "Number of seconds to shrink out the object's image when it's removed from scene. Use zero for no shrink out.", float, 2.0); 
%template.addBehaviorField(noGrowInCollision, "Suppress collisions when this object is growing in.  Note that there are never collisions when object is shrinking out.", bool, false);     
%template.addBehaviorField(shrinkOutSetAtRest, "When object shrinks out, set it at rest", bool, true);

function GrowShrinkBehavior::onAddToScene(%this)
{
   if (%this.GrowInTime)
   {
      %this.owner.visible = 0;
      if (%this.originalSize $= "")
      {
         %this.originalSize = %this.owner.getSize();
      }
      %this.schedule(1,startGrowShrinkIn);
   }  
}

function GrowShrinkBehavior::onNextLife(%this)
{
   %this.onAddToScene();
}

function GrowShrinkBehavior::startGrowShrinkIn(%this)
{
   %this.owner.visible = 1;
   if (!%this.owner.enabled) return;
   if (!%this.growInTime) return;
   if (%this.noGrowInCollision)
   {
      if (%this.originalCollisionSettings $= "")
      {
         %this.originalCollisionSettings = %this.owner.getCollisionActive();
      }
      %this.owner.setCollisionActive(0,0);
   }    
   %this.shrinkingOut = false;
   %this.owner.setSize("0 0");
   %this.owner.sizeTo(%this.originalSize, getWord(%this.originalSize, 0) / %this.growInTime, true, %this.noGrowInCollision, true);
   %this.isSizing = true;
}

function GrowShrinkBehavior::onSizeTarget(%this)
{
   if (!%this.isSizing) return;
   if (%this.shrinkingOut) 
   {
      %this.owner.safedelete();
   }
   else if (%this.noGrowInCollision)
   {
      %this.owner.setCollisionActive( getWord(%this.originalCollisionSettings,0), getWord(%this.originalCollisionSettings,1));
      %this.originalCollisionSettings = "";
   }
   %this.isSizing = false;
}

function GrowShrinkBehavior::onRemove(%this)
{
   %this.shrinkOut();
}

function GrowShrinkBehavior::onKilledByDamage(%this, %amount, %assailant, %healthRemaining, %livesRemaining)
{
   %this.shrinkOut();
   %this.owner.setSize(%this.originalSize);
}

function GrowShrinkBehavior::shrinkOut(%this)
{
   if (!%this.shrinkOutTime) return;
   if (%this.owner.isClone) return;
   if (isObject(%this.clone)) return; // in case something already called this
   if (isObject(%this.owner.scenegraph))
   {
      if (%this.ShrinkOutTime)
      {
         %clone = %this.owner.clone(0);
         %instance = growShrinkBehavior.createInstance();
         %instance.shrinkingout = true;
         %instance.growintime = 0;
         %clone.addBehavior( %instance);
         %clone.position = %this.owner.position;
         if (%this.ShrinkOutSetAtRest) { %clone.setAtRest();}
         %clone.sizeTo( "0 0", getWord(%this.owner.size, 0) / %this.shrinkOutTime, true, true, true);
         %instance.isSizing = true;
         %clone.isClone = true;
         %this.clone = %clone;
      }
   }
}


