from mygame.maingame import *

_pug = True

if __name__ == '__main__': 
    from mygame.puginterface import init_pug
    if _pug:
        init_pug()
    else:
        game()
    
    