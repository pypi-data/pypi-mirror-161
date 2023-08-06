from wx import *
import wx
from tkinter import *
def TK():
    pass
def WX():
    pass
class mainApp(App):
    def __enter__(self):
        return self
    def __exit__(self,*awgs):
        self.MainLoop()
        return True
class mainTk(Tk):
    def __enter__(self):
        return self
    def __exit__(self,*awgs):
        self.mainloop()
        return True
class window():
    def __init__(self,method=TK,title=None,pos=(-1,-1),size=None):
        if title is None:
            title=method.__name__ 
        if method==TK:
            self.root=Tk()
            self.root.title(title)
            if size is not None:
                self.root.geometry("%dx%d+%d+%d"%(size+pos))
            self.root.mainloop()
        elif method==WX:
            self.app=wx.App()
            if size is None:
                size=(-1,-1)
            self.win=wx.Frame(None,title=title,pos=pos,size=size)
            self.win.Show()
            self.app.MainLoop()
if __name__=="__main__":
    with mainApp() as app:
        win0=wx.Frame(None,title="wx")
        win0.Show()
    with mainTk() as win1:
        pass
    window(title="tk")
    window(method=WX,title="wx")
