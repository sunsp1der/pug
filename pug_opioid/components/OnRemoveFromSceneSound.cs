//----------------------------------------------------------------------------------
//Behavior Information
//----------------------------------------------------------------------------------
if (isObject(onRemoveFromSceneSoundBehavior))
{
   onRemoveFromSceneSoundBehavior.delete();
}

//create behavior
%template = new BehaviorTemplate(onRemoveFromSceneSoundBehavior);

%template.friendlyName = "OnRemoveFromScene Sound";
%template.behaviorType = "Sound";
%template.description = "Play a sound when the object is removed from the scene.";

//define fields
%template.addBehaviorField(sound,"The sound to play","sound","");
   
//----------------------------------------------------------------------------------
//Behavior Code
//----------------------------------------------------------------------------------s

function onRemoveFromSceneSoundBehavior::onRemoveFromScene(%this)
{
   if (isObject(%this.sound)) alxPlay(%this.sound);
}