//-----------------------------------------------------------------------------
// Fade.cs
//
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(FadeBehavior))
{
   FadeBehavior.delete();
}

%template = new BehaviorTemplate(FadeBehavior);
%template.friendlyName = "Fade";
%template.behaviorType = "Effect";
%template.description  = "Fade this object in when spawned and/or out when deleted";

%template.addBehaviorField(fadeInTime, "Number of seconds to fade in the object when it's added to scene. Use zero for no fade.", float, 2.0);      
%template.addBehaviorField(fadeOutTime, "Number of seconds to fade out the object's image when it's removed from scene. Use zero for no fade.", float, 2.0); 
%template.addBehaviorField(noFadeInCollision, "Suppress collisions when this object is fading in.  Note that there are never collisions when object is fading out.", bool, false);     
%template.addBehaviorField(fadeOutSetAtRest, "When object fades out, set it at rest", bool, true);

function FadeBehavior::onAddToScene(%this)
{  
   if (%this.fadeInTime)
   {
      %this.owner.visible = 0;
      if (%this.owner.fadeBase $= "")
      {
         %this.owner.fadeBase = %this.owner.getBlendAlpha();
      }
      %this.schedule(1,startFadeIn);
   }
}

function FadeBehavior::onNextLife(%this)
{ 
   %this.onAddToScene();
}

function FadeBehavior::startFadeIn(%this)
{
   %this.owner.visible = 1;
   if (!%this.fadeInTime) return;
   if (!%this.owner.enabled) return;
   if (%this.noFadeInCollision)
   {
      if (%this.originalCollisionSettings $= "")
      {
         %this.originalCollisionSettings = %this.owner.getCollisionActive();
      }
      %this.owner.setCollisionActive(0, 0);
   }   
   %this.owner.fadeIn( %this.fadeInTime, true, "CALLBACK");
   %this.isFading = true;
}

function FadeBehavior::onFadeInComplete(%this)
{
   if (!%this.isFading) return;
   %this.isFading = false;
   if (%this.noFadeInCollision)
   {
      %this.owner.setCollisionActive( getWord(%this.originalCollisionSettings,0), getWord(%this.originalCollisionSettings,1));
      %this.originalCollisionSettings = "";
   }
}

function FadeBehavior::onRemove(%this)
{
   %this.doFadeOut();
}

function FadeBehavior::onKilledByDamage(%this)
{
   %this.doFadeOut();
   %this.owner.setBlendAlpha(%this.owner.fadeBase);
}

function FadeBehavior::doFadeOut(%this)
{
   if (!%this.fadeOutTime) return;
   if (isObject(%this.clone)) return; // in case we're already fading
   if (isObject(%this.owner.scenegraph))
   {
      if (%this.fadeOutTime)
      {
         %clone = %this.owner.clone(0);
         %clone.position = %this.owner.position;
         if (%this.fadeOutSetAtRest) { %clone.setAtRest();}
         %clone.fadeOut( %this.fadeOutTime, DELETE);
         %this.clone = %clone;
      }
   }
}