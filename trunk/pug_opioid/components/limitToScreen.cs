//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(limitToScreenBehavior))
{
   limitToScreenBehavior.delete();
}   

%template = new BehaviorTemplate(limitToScreenBehavior);

%template.friendlyName = "Limit To Screen";
%template.behaviorType = "Gameplay";
%template.description  = "Keeps the object on screen by setting the object's world limits to the camera view.";

%template.addBehaviorField(edgeMode, "What to do when object reaches edge of screen.", enum, CLAMP, "NULL" TAB "CLAMP" TAB "BOUNCE" TAB "STICKY" TAB "KILL");
%template.addBehaviorField(expandArea, "Expand world limits so that the object will be completely offscreen",bool,false);
%template.addBehaviorField(callback, "Call onWorldLimits when object reaches edge of screen.", bool, true);

function limitToScreenBehavior::onAddToScene(%this)
{
   %this.schedule(0, setupLimit);
}

function limitToScreenBehavior::setupLimit(%this)
{
   if (!%this.owner.enabled) {return;}
   %area = $DEFAULTSCENEWINDOW.getCurrentCameraArea();
   if (%this.expandArea)
   {
      %expandSize = mSqrt(mPow(%this.owner.getSizeX(),2) + mPow(%this.owner.getSizeY(),2)) * 2;
      %area = setWord(%area, 0, getWord(%area, 0) - %expandSize);
      %area = setWord(%area, 1, getWord(%area, 1) - %expandSize);
      %area = setWord(%area, 2, getWord(%area, 2) + %expandSize);
      %area = setWord(%area, 3, getWord(%area, 3) + %expandSize);
   }
   %this.owner.setWorldLimit(%this.edgeMode, %area,%this.callback || %this.getWorldLimitCallback());
}

