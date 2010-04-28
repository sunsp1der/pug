import pygame

# this needs to be imported before pygame is initialized
pygame.mixer.pre_init(22050,-16,2,1024)
SoundDict = {}

def get_sound( filename, tag=""):
    """get_sound( filename, tag=""):

filename: path to the sound file. mp3, wav, or midi
tag: if you want to create different sound objects with the same sound file, for
    instance if you wanted to change the volume of each individually, give them 
    all different tags.
""" 
    try:
        index = filename+tag
    except:
        index = ""
    sound = SoundDict.get(index, None)
    if sound is None:
        sound = SoundDict[index] = load_sound(filename)
    return sound

def load_sound(name):
    if not pygame.mixer:
        class NoneSound:
            def play(self): pass
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error, message:
        print 'Cannot load sound:', name
        raise SystemExit, message
    return sound    

