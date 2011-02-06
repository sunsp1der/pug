import wx

MAX_UNDOS = 333

class HistoryManager():
    def __init__(self):
        self.clear()
        
    def add(self, description, undo_fn, do_fn, id=None):
        """add(item, id=None)
    
Add an undo item to the undo list.
description: a simple, human readable description
unfo_fn: a callable that undoes the action
do_fn: a callable that redoes the action    
id: an optional id for grouping undo items. All consecutive undo items with the
    same id will be undone and redone as a group. A value of None always starts
    a new group. Single steps can be taken with small_undo and small_redo.
"""
        if self.index < self.save_point:
            self.save_point = -1
        self.list = self.list[:self.index]
        if id is None or id != self.last_id:
            self.list.append("*")
            self.index += 1
            self.last_id = id
        self.list.append((description, undo_fn,do_fn))
        self.index += 1
        if len(self.list) > MAX_UNDOS:
            mark2 = self.list.index("*",1)
            self.list = self.list[mark2:]
            if self.index >= mark2:
                self.index -= mark2
            else:
                self.index = 0
                
    def has_changes(self):
        "has_changes(): True if there are changes since last save_point call"
        return self.index != self.save_point
    
    def save_point(self):
        self.save_point = self.index
        
    def clear(self):
        self.list = []
        self.index = 0
        self.last_id = None
        self.save_point = 0
        
    def undo(self):
        "undo(): undo the most recent undo items to the next '*' mark"
        if wx.GetApp().busyState:
            return
        if self.index == 0:
            return
        while self.list[self.index-1] != "*":  
            self.index -= 1
            cmd_item = self.list[self.index]
            cmd_item[1]()
        self.index -= 1 # past '*' mark
        wx.GetApp().refresh()
        
    def small_undo(self):
        "small_undo(): undo the most recent undo item"
        if wx.GetApp().busyState:
            return
        if self.index == 0:
            return
        self.index -= 1
        cmd_item = self.list[self.index]
        cmd_item[1]()
        if self.list[self.index-1] == "*":
            self.index -= 1
        wx.GetApp().refresh()
        
    def redo(self):
        "redo(): redo the most recent undone items to the next '*' mark"
        if wx.GetApp().busyState:
            return
        if self.index == len(self.list):
            return
        if self.list[self.index] == "*":
            self.index += 1 # skip '*' mark
        while self.index < len(self.list) and \
                self.list[self.index] != "*":
            cmd_item = self.list[self.index]
            cmd_item[2]()
            self.index += 1
        wx.GetApp().refresh()
        
    def small_redo(self):
        "small_redo(): redo the most recent undone item"
        if wx.GetApp().busyState:
            return
        if self.index == len(self.list):
            return
        if self.list[self.index] == "*":
            self.index += 1 # skip '*' mark        
        cmd_item = self.list[self.index]
        cmd_item[2]()
        self.index += 1
        if self.index < len(self.list) and self.list[self.index] == "*":
            self.index += 1
        wx.GetApp().refresh()        
                