//----------------------------------------------------------------------------------
//Behavior Information
//----------------------------------------------------------------------------------
if (isObject(onAddToSceneSoundBehavior))
{
   onAddToSceneSoundBehavior.delete();
}

//create behavior
%template = new BehaviorTemplate(onAddToSceneSoundBehavior);

%template.friendlyName = "onAddToScene Sound";
%template.behaviorType = "Sound";
%template.description = "Play a sound when the object is added to the scene.";

//define fields
%template.addBehaviorField(sound,"The sound to play","sound","");
   
//----------------------------------------------------------------------------------
//Behavior Code
//----------------------------------------------------------------------------------s

function onAddToSceneSoundBehavior::onAddToScene(%this)
{
   %this.schedule(1, playSound);
}

function onAddToSceneSoundBehavior::playSound(%this)
{
   if (%this.owner.enabled && isObject(%this.sound))
      alxPlay(%this.sound);
}