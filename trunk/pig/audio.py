import pygame
import os

SoundDict = {}

def get_sound( filename, tag=""):
    """get_sound( filename, tag=""):

filename: path to the sound file. mp3, wav, or midi
tag: if you want to create different sound objects with the same sound file, for
    instance if you wanted to change the volume of each individually, give them 
    all different tags.
""" 
    index = filename+tag
    sound = SoundDict.get(index, None)
    if sound is None:
        sound = SoundDict[index] = load_sound(filename)
    return sound

def load_sound(name):
    if not pygame.mixer:
        class NoneSound:
            def play(self): pass
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', name
        raise SystemExit, message
    return sound    

