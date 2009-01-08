import Opioid2D

import wx

import pug_opioid

from Example_Project.scenes.Diagonals import Diagonals
from Example_Project.scenes.Jumpers import Jumpers
from Example_Project.scenes.Three import Three

x = 100
y = 100
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

startScene = Three

Opioid2D.Display.init((800, 600), title='Scene')
Opioid2D.Director.start_game = True
import threading
t = threading.Thread(target=Opioid2D.Director.Run,args=(Three,))
t.start()
import pygame
import time
pygame.display.iconify()
time.sleep(1)
print pygame.display.Info()
pygame.display.set_mode((800,600))
#Opioid2D.Display.init((800, 600), title='Scene')
dict = pygame.display.get_wm_info()

#dict['display'])
#Opioid2D.Director.run(startScene)
#pug.frame(a)#dict['display'])

