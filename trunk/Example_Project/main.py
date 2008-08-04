import wx
import Opioid2D
from Example_Project.scenes.pug_action_timing import TimingScene

wxapp = wx.PySimpleApp()

frame = wx.Frame(None)
widget = wx.Button(frame)
frame.Show()
Opioid2D.Display.init((800, 600), title='Scene')
Opioid2D.Director.run(TimingScene)
wxapp.MainLoop()
