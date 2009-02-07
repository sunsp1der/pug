//-----------------------------------------------------------------------------
// Spider's TGB PowerPack
// Copyright (C) Ivan Spider DelSol
//-----------------------------------------------------------------------------
      
if (isObject(ReplaceWithRandomObjectzBehavior))
{
   ReplaceWithRandomObjectBehavior.delete();
}

%template = new BehaviorTemplate(ReplaceWithRandomObjectBehavior);

%template.friendlyName = "Replace With Random Object";
%template.behaviorType = "Spawn";
%template.description  = "When this object is added to the scene, it replaces itself with a random object. 'Weight' works as follows: if you have objects A, B, and C with weights 4, 1, and 1, object A will be chosen 4 out of 6 times amd objects B and C will be chosen 1 out of 6 times. This behavior can be cascaded for more possibilities.";

%template.addBehaviorField(object1, "Possible replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(weight1, "Selection weight", int, 1);
%template.addBehaviorField(object2, "Possible replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(weight2, "Selection weight", int, 1);
%template.addBehaviorField(object3, "Possible replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(weight3, "Selection weight", int, 1);
%template.addBehaviorField(object4, "Possible replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(weight4, "Selection weight", int, 1);
%template.addBehaviorField(object5, "Possible replacement object", object, "", t2dSceneObject);
%template.addBehaviorField(weight5, "Selection weight", int, 1);

function ReplaceWithRandomObjectBehavior::onLevelLoaded(%this)
{
   if (%this.randListCount $= "")
   {
      %this.randListCount = 0;
      for(%i = 1; %i <= 5; %i++)
      {
         eval( "%object = %this.object"@%i@";");
         if (isObject(%object))
         {
            eval( "%weight = %this.weight"@%i@";");
            for(%j = 0; %j < %weight; %j++)
            {
               %this.randList[%this.randListCount] = %object;
               %this.randListCount++;
            }
         }
      }
   }
}

function ReplaceWithRandomObjectBehavior::onAddToScene(%this)
{
   %this.schedule(1,doSwapOut);
}

function ReplaceWithRandomObjectBehavior::doSwapOut(%this)
{
   if (!%this.owner.enabled) return;
   
   %swapObject = %this.randList[ getRandom( %this.randListCount-1)];
   %newObject = %swapObject.cloneWithBehaviors();
   %newObject.position = %this.owner.position;
   %this.owner.safeDelete();
}