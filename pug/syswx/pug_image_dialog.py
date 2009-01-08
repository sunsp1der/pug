import wx

from wx.lib.imagebrowser import ImageDialog 

class PugImageDialog(ImageDialog):
    def __init__(self, *args, **kwargs):
        ImageDialog.__init__(self,*args,**kwargs)
        wx.TheColourDatabase.AddColour('WEIRDGREY',wx.Colour(209,211,231,255))
        self.image_view.back_color = "WEIRDGREY"
    def SetSelected(self, val):
        """Select the first list item equal to val"""
        num = self.fl_list.index(val)
        self.tb.Select(num)
        self.SetListValue(num)
    def GetFiles(self):
        """Get the file list using directory and extensions"""
        #Fix a bug in wx that shows all files twice and .* files
        ImageDialog.GetFiles(self)
        newlist = []
        for item in self.fl_list:
            if item[0:1] == "." and item != "." and item != "..":
                continue
            newlist.append(item)
        self.fl_list = list(set(newlist))
        self.fl_list.sort()