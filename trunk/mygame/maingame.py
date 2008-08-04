"""An example pygame application set up to use the editor 
"""

import pygame
from pygame.locals import *
from pug.component.test import *

from testobject import fake

#------------------------------------------------------------------------------ 
class game(): 
    """Root game object"""
    def __init__( self, screen = None, autorun = True):
        """Initialize the game
        
screen: the pygame screen. 
autoRun: starts the game immediately upon creation
"""
        pygame.init()
        pygame.display.set_caption('mygame')
        if (screen == None):
            screen = pygame.display.set_mode((250,100))
        self.screen = screen 
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        self.background = background
        self.font = pygame.font.Font(None, 36)
        self._color = 1
        self.colordelta = 0.1
        self.message = None
        self.dummy = fake()
        self.dummy.back = self.background
        self.paused = False
        if autorun:
            self.mainloop()
        
    def mainloop(self): 
        """Execute loop() until QUIT event"""
        self.autoLoop = True
        while self.autoLoop: 
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                    continue
            if self.paused is False:
                self.mainloop_code() 
        pygame.quit()
                
    def quit(self, immediate=False):
        self.autoLoop = False
        if immediate:
            pygame.quit()
            
    def pause(self, doPause = True):
        self.paused = doPause
                                
    def mainloop_code(self): #pee
        """Main game loop"""        
        self._color += self.colordelta
        if self._color >= 255 or self._color <= 0: 
            self.colordelta *= -1
            self._color += self.colordelta
        # Fill background
        self.background.fill((self._color, self._color, self._color))
        textcolor = 255 - self._color

        # Display some text
        text = self.font.render(str(self.message), 1, 
                                (textcolor, textcolor, textcolor))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos.centery = self.background.get_rect().centery
        self.background.blit(text, textpos)                    

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()    
        
    def messageSwitch(self):
        """messageSwitch(self)
        
Change the message string
"""
        if self.message == "Hello, Utopia":
            self.message = "Goodbye, Fascism"
        else:
            self.message = "Hello, Utopia"
            
    def changeMessageTo(self, msg = "Bye World"):
        """changeMessageTo(self, msg="Bye World")
        
msg becomes new message"""
        self.message = msg
         
if __name__ == '__main__': 
    game()