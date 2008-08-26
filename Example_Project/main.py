import Opioid2D
import wx
from Example_Project.scenes.Diagonals2 import Diagonals2

startScene = Diagonals2

Opioid2D.Display.init((800, 600), title='Scene')
Opioid2D.Director.start_game = True
Opioid2D.Director.run(startScene)
