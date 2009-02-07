//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(FaceMouseBehavior))
{
   FaceMouseBehavior.delete();
}

%template = new BehaviorTemplate(FaceMouseBehavior);

%template.friendlyName = "Face Mouse";
%template.behaviorType = "Input";
%template.description  = "Set the object to always face the mouse";

%template.addBehaviorField(turnSpeed, "The speed to rotate at (degrees per second). Use 0 to snap", float, 0.0);
%template.addBehaviorField(rotationOffset, "The rotation offset (degrees)", float, 0.0);

function FaceMouseBehavior::onAddToScene(%this)
{
   %this.owner.setUseMouseEvents(true);
}

function FaceMouseBehavior::onAddToScene(%this, %scenegraph)
{
   %this.owner.setMouseLocked(true);
}

function FaceMouseBehavior::onMouseMove(%this, %modifier, %worldPos)
{
   %vector = t2dVectorSub(%worldPos, %this.owner.position);
   %targetRotation = mRadToDeg(mAtan(%vector.y, %vector.x)) + %this.rotationOffset + 90 ;
   
   if (%this.turnSpeed == 0)
      %this.owner.setRotation(%targetRotation);
   else
      %this.owner.rotateTo(%targetRotation, %this.turnSpeed, true, false, true, 0.1);
}

function FaceMouseBehavior::onMouseDragged(%this, %modifier, %worldPos)
{
   %this.onMouseMove(%modifier, %worldPos);
}
