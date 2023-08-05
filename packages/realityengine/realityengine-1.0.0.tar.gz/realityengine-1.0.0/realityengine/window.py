from time import sleep
from tkinter import BOTH, YES, TclError, Tk, PhotoImage

from realityengine.util import InvalidValueError, InvalidPathError, ResizingCanvas
from realityengine.game_object import gameobjects

import sys

class Window:
    def __init__(self, width: int, height: int, title: str = "RealityEngine Window", bg: str="#000000", FPS: int=15):
        """
        Creates the main window and sets up the canvas.\n
        \n
        `title` - The main title of the window.\n
        `width` - The Width of the window in pixels.\n
        `height` -  The height of the window in pixels.
        """
        self.title = title
        self.width = width
        self.height = height
        self.bg = bg
        self.FPS = FPS

        self.window = Tk()
        self.window.configure(background=bg)
        self.window.wm_title(title)
        self.window.geometry(f"{self.width}x{self.height}")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.canvas = ResizingCanvas(self.window, width=self.width, height=self.height, bg=self.bg, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=YES)

        self.custom_update = None

        self.open = False

    def set_custom_update(self, method):
        """
        Sets the method to be run when update occurs to the `method` argument.

        Arguments:
            `method` | The function to be set as the custom update.
        """
        self.custom_update = method

    def resize(self, width: int, height: int):
        """
        Sets the size of the window.

        Arguments:
            `width`  | The new width of the window.\n
            `height` | The new height of the window.
        """
        self.window.geometry(f"{width}x{height}")
        self.width = width
        self.height = height

    def clock(self, fps):
        """
        Sets the clock speed of the window.

        Arguments:
            `fps` | The clock speed.
        """
        self.FPS = fps

    def run(self):
        """
        Starts the main window and sets up window events.
        """
        self.open = True
        self.window.after( self.FPS, self.update)
        self.window.mainloop()

    def clear(self):
        """
        Clears the window by un-rendering all drawn objects.
        """
        try:
            self.canvas.delete("all")
        except:
            pass

    def update(self):
        global run_self
        """
        Clears the screen and updates then draws all active gameobjects.
        """
        self.clear()

        if self.open == False:
            self.run()

        for go in gameobjects:
            go.update()
            transform = go.transform
            if go.shape == "rectangle":
                self.draw_rect(transform.top_corner[0], transform.top_corner[1], transform.bottom_corner[0], transform.bottom_corner[1], "", go.colour, go.layer)
            elif go.shape == "circle":
                self.draw_oval(transform.top_corner[0], transform.top_corner[1], transform.bottom_corner[0], transform.bottom_corner[1], 0, go.colour, go.layer)
            else:
                raise InvalidValueError(go.shape)

        if self.custom_update:
            self.custom_update()
        
        self.window.after(self.FPS, self.update)

    def set_title(self, title: str):
        """
        Sets the title of the window to the `title` argument.
        """
        self.window.wm_title(title)
        self.title = title

    def set_bg(self, bg: str):
        """
        Sets the background of the window to the `bg` argument.
        """
        try:
            self.window.configure(background=bg)
            self.canvas.configure(bg=bg)
            self.bg = bg
        except TclError:
            raise InvalidValueError(bg)

    def set_icon(self, icon_path: str):
        """
        Sets the icon of the window to the `icon_path` argument.
        """
        try:
            self.window.iconphoto(True, PhotoImage(file=icon_path))
        except TclError:
            raise InvalidPathError(icon_path)

    def set_resizable(self, resize_type: str):
        if resize_type == "none":
            self.window.resizable(False, False)
        elif resize_type == "x-axis":
            self.window.resizable(True, False)
        elif resize_type == "y-axis":
            self.window.resizable(False, True)
        elif resize_type == "both":
            self.window.resizable(True, True)

    def draw_rect(self, x_0: int, y_0: int, x_1: int, y_1: int, outline: str, colour: str, layer: str = "front"):
        try:
            rect = self.canvas.create_rectangle(x_0, y_0, x_1, y_1, fill=colour, outline=outline)
            if layer == "front":
                self.canvas.tag_raise(rect)
            elif layer == "back":
                self.canvas.tag_lower(rect)
        except TclError:
            pass

    def draw_oval(self, x_0: int, y_0: int, x_1: int, y_1: int, width: int, fill: str, layer: str = "front"):
        try:
            oval = self.canvas.create_oval(x_0, y_0, x_1, y_1, width=width, fill=fill)
            if layer == "front":
                self.canvas.tag_raise(oval)
            elif layer == "back":
                self.canvas.tag_lower(oval)
        except TclError:
            pass

    def draw_text(self, x: int, y: int, text: str, foreground: str = "black", font: tuple = ("Helvetica 15 bold"), layer: str = "front"):
        try:
            text = self.canvas.create_text(x, y, text=text, fill=foreground, font=font)
            if layer == "front":
                self.canvas.tag_raise(text)
            elif layer == "back":
                self.canvas.tag_lower(text)
        except TclError:
            pass
    
    def get_width(self):
        """
        Returns the width of the window in pixels.
        """
        return self.width

    def get_height(self):
        """
        Returns the height of the window in pixels.
        """
        return self.height
    
    def get_size(self):
        """
        Returns a tuple with the width and height of the window.
        """
        return (self.width, self.height)

    def close(self):
        self.window.destroy()
        sys.exit()

    def bind_key(self, key: str, method):
        """ 
        Binds the specified key to the given function and passes the event.

        Arguments:
            `key`    | The key that is binded to the method.\n
            `method` | The mthod that is run when the key is pressed.
        """
        self.window.bind(key, lambda event: method(event))

    def get_all_gameobjects_with_tag(self, tag: str):
        gos = []

        for go in gameobjects:
            if tag in go.tags:
                gos.append(go)

        return gos

    def halt_until_key(self, key: str):
        """
        Halt the program until the specified key is pressed.

        Arguments:
            `key` | The key that needs to be pressed.
        """
        halted = True

        def change(e):
            global halted
            if e.keysym == "<Return>":
                halted = False

        self.window.bind(key, lambda event: change)

        while not halted:
            sleep(0.2)