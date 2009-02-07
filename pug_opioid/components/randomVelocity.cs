//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------

if (isObject(RandomVelocityBehavior))
{
   RandomVelocityBehavior.delete();
}

%template = new BehaviorTemplate(RandomVelocityBehavior);

%template.friendlyName = "Random Velocity";
%template.behaviorType = "AI";
%template.description  = "Sets a random velocity, rotation and spin on the object when it spawns";

%template.addBehaviorField(minAngle, "The minimum angle of the object's direction (degrees)", float, 0.0);
%template.addBehaviorField(maxAngle, "The maximum angle of the object's direction (degrees)", float, 360.0);
%template.addBehaviorField(minSpeed, "The minimum speed of the object (world units per second)", float, 10.0);
%template.addBehaviorField(maxSpeed, "The maximum speed of the object (world units per second)", float, 25.0);
%template.addBehaviorField(minRotationSpeed, "The minimum rotation speed of the object (degrees)", float, 0.0);
%template.addBehaviorField(maxRotationSpeed, "The maximum rotation speed of the object (degrees)", float, 0.0);
%template.addBehaviorField(alignRotation, "After spawning, align object's rotation to direction of movement.", bool,1);
%template.addBehaviorField(addVelocity, "Add this velocity to any other velocity the object has", bool, 1);

function RandomVelocityBehavior::onAddToScene(%this, %scenegraph)
{
   if (%this.addVelocity)
   {
      %currentV = %this.owner.getLinearVelocity();
      %currentR = %this.owner.getAngularVelocity();
   }
   else
   {
      %currentV = "0 0";
      %currentR = 0;
   }
   %direction = getRandom(%this.minAngle * 1000, %this.maxAngle * 1000);
   %speed = getRandom(%this.minSpeed * 1000, %this.maxSpeed * 1000);
   %this.owner.setLinearVelocityPolar(%direction * 0.001, %speed * 0.001);
   if (%this.addVelocity)
   {
      %addV = %this.owner.getLinearVelocity();
      %this.owner.setLinearVelocity(t2dVectorAdd(%addV,%currentV));
   }
   
   %rotation = getRandom(%this.minRotationSpeed * 1000, %this.maxRotationSpeed * 1000);
   %this.owner.setAngularVelocity(%rotation * 0.001 + %currentR);      

   if (%this.alignRotation)
   {
      %r = %this.schedule(0,alignRotation);
   }
}

function RandomVelocityBehavior::alignRotation(%this)
{
   %r = %this.owner.getLinearVelocityPolar();
   %this.owner.setRotation(getWord(%r,0));
}
