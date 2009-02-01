import os

import wx
from wx.lib.imagebrowser import ImageDialog, FindFiles, ID_CHECK_BG

class PugImageDialog(ImageDialog):
    def __init__(self, *args, **kwargs):
        ImageDialog.__init__(self,*args,**kwargs)
        self.image_view.SetBackgroundMode( ID_CHECK_BG)
    def SetSelected(self, val):
        """Select the first list item equal to val"""
        num = self.fl_list.index(val)
        self.tb.Select(num)
        self.SetListValue(num)
    def OnUpDirectory(self, event):
        if os.path.split(self.set_dir)[0] == '':
            self.set_dir = os.path.join(os.getcwd(),self.set_dir)
        ImageDialog.OnUpDirectory(self, event)
    def GetFiles(self):
        """Get the file list using directory and extensions"""
        #Fix a bug in wx that shows all files twice and .* files
        if self.fl_ext == "All":
            all_files = []

            if self.fl_types[-1:-1] == '*.*':
                allTypes = self.fl_types[1:-1]
            else:
                allTypes = self.fl_types[1:-1]
            for ftypes in allTypes:    # get list of all
                filter = self.fl_ext_types[ftypes]
                #print "filter = ", filter
                self.fl_val = FindFiles(self, self.set_dir, filter)
                all_files = all_files + self.fl_val.files   # add to list of files

            self.fl_list = all_files
        else:
            self.fl_val = FindFiles(self, self.set_dir, self.fl_ext)
            self.fl_list = self.fl_val.files
        # BUG FIX HERE
        newlist = []
        for item in self.fl_list:
            if item[0:1] == ".":
                continue
            newlist.append(item)
        self.fl_list = newlist
        self.fl_list = list(set(newlist)) # remove dupes
        # prepend the directories
        dirlist = []
        for item in self.fl_val.dirs:
            if item[0:1] == ".":
                continue
            dirlist.append(item)
        dirlist = list(set(dirlist))
        self.fl_val.dirs = dirlist
        # END BUg FIX
        
        self.fl_list.sort()     # sort the file list        
        self.fl_ndirs = len(self.fl_val.dirs)
        self.fl_list = sorted(self.fl_val.dirs) + self.fl_list

