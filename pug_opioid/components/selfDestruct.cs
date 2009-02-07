//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(SelfDestructBehavior))
{
   SelfDestructBehavior.delete();
}

%template = new BehaviorTemplate(SelfDestructBehavior);

%template.friendlyName = "Self Destruct";
%template.behaviorType = "Gameplay";
%template.description  = "Causes the object to self destruct after a specified event";

%template.addBehaviorField(fuseTime, "The time before the object will self destruct (seconds)", float, "2.0");
%template.addBehaviorField(deathEffect, "The particle effect to display when the countdown finishes", object, "", t2dParticleEffect);
%template.addBehaviorField(startOnAdd, "Start countdown when the object is created", bool, "1");
%template.addBehaviorField(startOnMouseDown, "Start countdown when the object is clicked on", bool, "0");
%template.addBehaviorField(startOnCollision, "Start countdown when the object collides", bool, "0");
%template.addBehaviorField(startOnWorldLimit, "Start countdown when the object hits its world limit", bool, "0");

function SelfDestructBehavior::onAddToScene(%this)
{
   // [Neo, 6/6/2007 - #3203]
   // setUseMouseEvents() etc need to be called on owner not %this
   if (%this.startOnMouseDown)
      %this.owner.setUseMouseEvents(true);
   
   if (%this.startOnCollision)
      %this.owner.collisionCallback = true;
   
   if (%this.startOnWorldLimit)
      %this.owner.worldLimitCallback = true;
      
   if (getWord(%this.owner.getWorldLimit, 0) $= "OFF") 
      %this.owner.setWorldLimit("NULL");
}

function SelfDestructBehavior::onAddToScene(%this, %scenegraph)
{
   if (%this.startOnAdd)
      %this.startCountdown(%this);
}

function SelfDestructBehavior::onCollision(%this, %dstObj, %srcRef, %dstRef, %time, %normal, %contactCount, %contacts)
{
   if (%this.startOnCollision)
      %this.startCountdown(%this);
}

function SelfDestructBehavior::onMouseDown(%this, %modifier, %worldPos)
{
   if (%this.startOnMouseDown)
      %this.startCountdown(%this);
}

function SelfDestructBehavior::onWorldLimit(%this, %mode, %side)
{
   if (%this.startOnWorldLimit)
      %this.startCountdown(%this);
}

function SelfDestructBehavior::startCountdown(%this)
{
   if (!isEventPending(%this.countdownSchedule))
      %this.countdownSchedule = %this.schedule(%this.fuseTime * 1000, "explode");
}

function SelfDestructBehavior::explode(%this)
{
   if (isObject(%this.deathEffect))
   {
      %explosion = %this.deathEffect.cloneWithBehaviors();
      %explosion.position = %this.owner.position;
      %explosion.setEffectLifeMode("Kill", 1.0);
      %explosion.playEffect();
   }
   
   %this.owner.safeDelete();
}
