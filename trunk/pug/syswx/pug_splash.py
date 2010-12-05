import wx

from pug.util import get_image_path

class PugSplash(wx.SplashScreen):
    """
Create a splash screen widget.
    """
    def __init__(self, parent=None):
        # This is a recipe to a the screen.
        # Modify the following variables as necessary.
        bitmap = wx.Bitmap(get_image_path('pug.png'), wx.BITMAP_TYPE_PNG)
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT |\
                        wx.NO_BORDER | wx.STAY_ON_TOP
        splashDuration = 1000 # milliseconds
        # Call the constructor with the above arguments in exactly the
        # following order.
        wx.SplashScreen.__init__(self, bitmap, splashStyle,
                                 splashDuration, parent)
        self.Hide()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()
#----------------------------------------------------------------------#

    def OnExit(self, evt):
        self.Destroy()
        evt.Skip()  # Make sure the default handler runs too...
#----------------------------------------------------------------------#