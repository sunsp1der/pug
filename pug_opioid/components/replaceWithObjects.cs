//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------
      
if (isObject(ReplaceWithObjectszBehavior))
{
   ReplaceWithObjectsBehavior.delete();
}

%template = new BehaviorTemplate(ReplaceWithObjectsBehavior);

%template.friendlyName = "Replace With Objects";
%template.behaviorType = "Spawn";
%template.description  = "When this object is added to the scene, it replaces itself with an object or objects. This behavior can be cascaded for more possibilities.";

%template.addBehaviorField(object1, "Replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(object2, "Replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(object3, "Replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(object4, "Replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(object5, "Replacement object", object, "", t2dSceneObject);

function ReplaceWithObjectsBehavior::onAddToScene(%this)
{
   %this.schedule(1,doSwapOut);
}

function ReplaceWithObjectsBehavior::doSwapOut(%this)
{
   if (!%this.owner.enabled) return;
   
   for (%i = 1; %i < 6; %i++)
   {
      eval("%swapObject = %this.object" @ %i @";");
      if (isObject(%swapObject))
      {
         %newObject = %swapObject.cloneWithBehaviors();
         %newObject.position = %this.owner.position;
      }
   }
   %this.owner.safeDelete();
}