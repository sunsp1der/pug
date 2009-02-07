//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(ScreenWrapBehavior))
{
   ScreenWrapBehavior.delete();
}

%template = new BehaviorTemplate(ScreenWrapBehavior);

%template.friendlyName = "Screen Wrap";
%template.behaviorType = "Gameplay";
%template.description  = "Wrap the object to the other side when it leaves the screen.";

function ScreenWrapBehavior::onAddToScene( %this)
{
   %this.schedule(0,setupWrap);
}

function ScreenWrapBehavior::setupWrap(%this)
{
   if (!%this.owner.enabled) {return;}
   %area = $DEFAULTSCENEWINDOW.getCurrentCameraArea();
   %this.expandSize = %this.owner.getSizeX()>%this.owner.getSizeY()?%this.owner.getSizeX():%this.owner.getSizeY();
   %area = setWord(%area, 0, getWord(%area, 0) - %this.expandSize);
   %area = setWord(%area, 1, getWord(%area, 1) - %this.expandSize);
   %area = setWord(%area, 2, getWord(%area, 2) + %this.expandSize);
   %area = setWord(%area, 3, getWord(%area, 3) + %this.expandSize);
   %this.owner.setWorldLimit("NULL", %area, true);
}

function ScreenWrapBehavior::onWorldLimit(%this, %limitMode, %limit)
{
   switch$ (%limit)
   {
      case "left":
         if (%this.owner.getLinearVelocityX() < 0)
            %this.owner.setPositionX(getWord(%this.owner.getWorldLimit(), 3) - (%this.expandSize / 2));
      case "right":
         if (%this.owner.getLinearVelocityX() > 0)
            %this.owner.setPositionX(getWord(%this.owner.getWorldLimit(), 1) + (%this.expandSize / 2));
      case "top":
         if (%this.owner.getLinearVelocityY() < 0)
            %this.owner.setPositionY(getWord(%this.owner.getWorldLimit(), 4) - (%this.expandSize / 2));
      case "bottom":
         if (%this.owner.getLinearVelocityY() > 0)
            %this.owner.setPositionY(getWord(%this.owner.getWorldLimit(), 2) + (%this.expandSize / 2));
   }
}
