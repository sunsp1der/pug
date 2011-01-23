import pygame

from pug.util import destandardize_filename

# this needs to be imported before pygame is initialized
pygame.mixer.pre_init(22050,-16,2,1024)
SoundDict = {}

class NoneSound:
    def play(self): pass
    def stop(self): pass
    def fadeout(self): pass
    def set_volume(self): pass
    def get_volume(self): pass
    def get_num_channels(self): pass
    def get_length(self): pass
    def get_buffer(self): pass

def get_sound( filename, tag="", volume=1.0):
    """get_sound( filename, tag="", volume=1.0)->pygame.mixer.Sound object

Create a sound object with a 'play' method. If filename evaluates to False, a 
dummy sound object will be created that has a 'play' method that does nothing.

filename: path to the sound file. mp3, wav, or midi
tag: if you want to create different sound objects with the same sound file, you
    can give them different tags
volume: you can pass a float from 0 to 1 for the sound volume. A unique sound
    will be created with that volume. You can still set the volume of a sound,
    but that will change all sounds with this tag/volume combination.
""" 
    if not filename:
        return NoneSound()
    index = filename+"_"+tag+"_"+str(volume)
    sound = SoundDict.get(index, None)
    if sound is None:
        try:
            sound = SoundDict[index] = load_sound(filename)
        except:
            sound = SoundDict[index] = load_sound(
                                            destandardize_filename(filename))    
    sound.set_volume(volume)
    return sound

def load_sound(name):
    if not pygame.mixer:
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error, message:
        print 'Cannot load sound:', name, '\n', message
        return NoneSound()
#        raise SystemExit, message
    return sound    

