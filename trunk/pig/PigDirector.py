"""PigDirector.py

Hack in a few features necessary for the Opioid2D director to work with pug"""
import time
from inspect import isclass

import Opioid2D
from Opioid2D.internal.objectmgr import ObjectManager
from Opioid2D.public.Image import ImageMeta
from Opioid2D.public.ResourceManager import ResourceManager

old_ticks = now = frames = None

opioid_quit = Opioid2D.Director.quit
PigDirector = Opioid2D.Director

_DEBUG = False #

# this presents incorrect scene errors in code
PigDirector.scene = None

#hack for quitting pug when opioid quits
QUITTING = False
def pig_quit( query=True):
    """pig_quit( query=True)
    
query: if True, have the app confirm project closure.
"""
    if not query:
        return real_quit()
    global QUITTING
    try:
        import wx
        wx = wx
        if not wx.GetApp() or \
                not getattr(wx.GetApp().projectObject,'_initialized', False):
            if _DEBUG: print "PigDirector real_quit" 
            real_quit()
            return
        if not QUITTING:
            QUITTING = True
            app = wx.GetApp()
            if hasattr(app, '_evt_project_frame_close'):
                if _DEBUG: print "PigDirector _evt_project_frame_close"
                wx.CallAfter(app._evt_project_frame_close, query=query)
            return
    except:
        if _DEBUG: print "PigDirector except real_quit"
        real_quit() 
# set up our special quit
def real_quit():
    global QUITTING
    try:
        import wx     
        wx = wx  
        if _DEBUG: print "PigDirector.real_quit kill_subprocesses"
        wx.GetApp().get_project_object().kill_subprocesses()
        if _DEBUG: print "PigDirector.real_quit _evt_project_frame_close"
        wx.GetApp()._evt_project_frame_close(query=False)
    except:
        pass
    if not QUITTING:
        if _DEBUG: print "opioid_quit"
        opioid_quit()
#        import pygame
#        pygame.quit()
    QUITTING = True

PigDirector.quit = pig_quit # hack to make opioid quit=pugquit 
PigDirector.realquit = real_quit
    
#hack for running opioid with pause control
def newrun(initialScene, *args, **kw):
    """Run the Director mainloop until program exit
    """
    self = PigDirector
    try:
        # This is a long and ugly function that hasn't been splitted into smaller parts
        # because of performance considerations.
        
        import pygame
        pygame.init()
        from Opioid2D.public.Mouse import Mouse
        
        # Bind functions to local names in order to increase performance
        sleep = time.sleep
        throttle = pygame.time.Clock()
        flip = pygame.display.flip
        get_ticks = pygame.time.get_ticks
        cD = self._cDirector
        OM = ObjectManager
        
        self._scene = None
        self.next_scene = None
        self.next_state = None
        self.paused = False
        
        now = get_ticks()
        cD.Start(now)

        self.set_scene(initialScene, *args, **kw)
        
        self._running = True            
        start = time.time()
        frames = 0
        self.delta = 0
        ticker = cD.GetTicker()
        old_ticks = now
        self.now = now
        
        # Preload Image subclasses that have been imported and that
        # contain the preload flag.
        for img in ImageMeta.subclasses:
            if img.preload:
                ResourceManager.get_image(img)
                
        while self._running:
            # Trigger possible scene change at the beginning of a new frame
            if self.next_scene is not None:
                self._change_scene()
            
            # Time delta calculation
            ticks = get_ticks()
            self.delta = delta = min(ticks-old_ticks, 25) # limit the virtual clock to a max. advance of 25ms per frame
            old_ticks = ticks
            self.now = now = now + delta
            cD.Iterate(now)
            
            scene = self._scene
            cscene = scene._cObj
            if not self.paused:
                cscene.Tick()
                
                # Call Scene tick callbacks
                if scene._tickfunc is not None:
                    scene._tickfunc()
                if ticker.realTick:
                    if scene._realtickfunc is not None:
                        scene._realtickfunc()
                
            # Event handling
            ev = pygame.event.get()
            if scene.mouse_manager is not None:
                scene.mouse_manager.tick(ev)
            scene._handle_events(ev)

            # Manage state change within the scene
            while self.next_state is not None:
                s = self.next_state
                self.next_state = None
                self.scene._init_state(s)            
                        
            # Update the screen
            cD.RenderFrame()
            
            # render software mouse cursor
            ms = Mouse._sprite
            if ms:
                ms.position = Mouse.position
                ms._cObj.TraverseFree()
            
            flip()
            
            # Purge managed C++ objects that have been killed on the C++ side.
            OM.purge()
            
            frames += 1
            throttle.tick(100) # limit FPS to 100 for lower CPU usage
        end = time.time()
    finally:
        from Opioid2D import _opi2d
        _opi2d.cleanup()
    return frames/(end-start)    

PigDirector.run = newrun
PigDirector.paused = False

def switch_scene_to( new_scene):
    if not isclass(new_scene):
        try:
            exec("from scenes."+ new_scene +" import "+ new_scene +" as target")
        except:
            raise
    else:
        target = new_scene
    self = PigDirector
    self.set_scene( target)
    
PigDirector.switch_scene_to = switch_scene_to
    

def opioid_tick():
    import pygame
    from Opioid2D.public.Mouse import Mouse
    self = Opioid2D.Director
    throttle = pygame.time.Clock()
    flip = pygame.display.flip
    get_ticks = pygame.time.get_ticks
    cD = self._cDirector
    OM = ObjectManager
    ticker = cD.GetTicker()
    global old_ticks, now, frames
    # Trigger possible scene change at the beginning of a new frame
    if self.next_scene is not None:
        self._change_scene()
    
    # Time delta calculation
    ticks = get_ticks()
    self.delta = delta = min(ticks-old_ticks, 25) # limit the virtual clock to a max. advance of 25ms per frame
    old_ticks = ticks
    self.now = now = now + delta
    cD.Iterate(now)
    
    scene = self._scene
    cscene = scene._cObj
    cscene.Tick()
    
    # Event handling
    ev = pygame.event.get()
    if scene.mouse_manager is not None:
        scene.mouse_manager.tick(ev)
    scene._handle_events(ev)
    
    # Call Scene tick callbacks
    if scene._tickfunc is not None:
        scene._tickfunc()
    if ticker.realTick:
        if scene._realtickfunc is not None:
            scene._realtickfunc()
    
    # Manage state change within the scene
    while self.next_state is not None:
        s = self.next_state
        self.next_state = None
        self.scene._init_state(s)
    
    # Update the screen
    cD.RenderFrame()
    
    # render software mouse cursor
    ms = Mouse._sprite
    if ms:
        ms.position = Mouse.position
        ms._cObj.TraverseFree()
    
    flip()
    
    # Purge managed C++ objects that have been killed on the C++ side.
    OM.purge()
    
    frames += 1
    throttle.tick(100) # limit FPS to 100 for lower CPU usage