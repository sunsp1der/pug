import dummy_threading as threading

import pygame
import pug

from mygame.maingame import game
    
class MyInterface():
    """Derive our own interface so we can add a couple functions"""
    def __init__(self):
        self.game = None
        self.start()
#        pug.ProjectInterface.__init__(self)
    def start(self):
        if self.game:
            self.game.quit(True)
        self.game = game( autorun = False)
        self.dummy = self.game.dummy
        self.dummy.mygame = self.game
        self.dummy.interface = self
#        self.game.pause()
        mainthread = threading.Thread(target=self.game.mainloop)
        mainthread.start()
    def play (self):
        """Unpause the project"""
        self.game.pause(False)
    def pause(self):
        """Pause the project"""
        self.game.pause(True)        
    def quit(self):
        """The project's quit function"""
        self.game.quit() 
        self.game=None    
    
def init_pug():
    
    interface = MyInterface()
    pug.App( projectObject=interface, projectName='MyGame')      
      
    
if __name__ == '__main__':
    init_pug()