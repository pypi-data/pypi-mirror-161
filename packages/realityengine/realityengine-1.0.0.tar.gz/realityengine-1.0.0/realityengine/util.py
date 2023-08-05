from tkinter import Canvas

class InvalidValueError(Exception):
    def __init__(self, value):
        self.value = value
        self.err = f"Invalid value {value}."
        super().__init__(self.err)


class InvalidPathError(Exception):
    def __init__(self, value):
        self.value = value
        self.err = f"Can't find path {value}."
        super().__init__(self.err)
        

class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)