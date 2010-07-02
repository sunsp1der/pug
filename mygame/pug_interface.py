import thread

import pygame
import pug

from mygame.maingame import game
    
class MyInterface(pug.ProjectInterface):
    """Derive our own interface so we can add a couple functions"""
    def __init__(self):
        self.game = None
        self.start()
        pug.ProjectInterface.__init__(self)
    def start(self):
        """Start the game again after 'quit'"""
        if self.game:
            return
        self.game = game( autorun = False)
        self.dummy = self.game.dummy
        self.dummy.mygame = self.game
        self.dummy.interface = self
        self.game.pause()
        thread.start_new_thread(self.game.mainloop,())
    def play (self):
        """Unpause the project"""
        self.game.pause(False)
    def pause(self):
        """Pause the project"""
        self.game.pause(True)        
    def quit(self):
        """The project's quit function"""
        self.game.quit(True) 
        self.game=None
    def _on_pug_quit(self):
        self.game.quit(True)    
    
def init_pug():
    interface = MyInterface()
    pug.App( projectObject=interface, projectObjectName='MyGame')
    
if __name__ == '__main__':
    init_pug()
