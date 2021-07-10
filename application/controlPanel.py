from tkinter import *
from tkinter.font import Font
from application.style import Style
from PIL import ImageTk, Image

class ControlPanel(Frame):
    def __init__(self, master, controlPackSide = LEFT, img_size = 20, btn_size = 40):
        super().__init__(master=master, background=Style.back_color)

        self.controlPackSide = controlPackSide
        self.img_size = img_size
        self.btn_size = btn_size

        self.controls = {}
        self.activeControl = None
        self.enable = False

    def enablePanel(self):
        self.enable = True
    
    def disablePanel(self):
        self.enable = False

    def addControl(self, id, icon, command):
        if not (id in self.controls):
            img = Image.open(icon)
            img = img.resize((self.img_size, self.img_size), Image.ANTIALIAS)
            tmp = ImageTk.PhotoImage(img)

            control = Button(self, border=0, image=tmp, width=self.btn_size, height=self.btn_size)
            control.image = tmp
            control.configure(command = lambda: self.on_control_selected(id, command))

            control.configure(background = Style.back_color, activebackground=Style.back_color)

            self.controls[id] = control

            control.pack(side=self.controlPackSide)

    def setActive(self, controlID):
        if controlID in self.controls:
            control = self.controls[controlID]
            if self.activeControl != None:
                self.controls[self.activeControl].configure(background=Style.back_color)
            
            control.configure(background = Style.back_color_lighter)
            self.activeControl = controlID

    def isActive(self, controlID):
        return self.activeControl != None and self.activeControl == controlID

    def on_control_selected(self, controlID, command):
        if self.enable:
            if self.activeControl != None:
                self.controls[self.activeControl].configure(background=Style.back_color)
                
            self.controls[controlID].configure(background = Style.back_color_lighter)
            self.activeControl = controlID
            command()

    def show(self):
        pass

class DetectionControlPanel(ControlPanel):
    def __init__(self, master, on_start = lambda:(), on_pause = lambda:(), on_stop = lambda:()):
        super().__init__(master=master)
        self.addControl("start", "assets/start_capture.png", on_start)
        self.addControl("pause", "assets/pause_capture.png", on_pause)
        self.addControl("stop", "assets/stop_capture.png", on_stop)

    def show(self, side = BOTTOM):
        self.pack(side=side, pady=(0,10))
        

class DetectionViewModePanel(ControlPanel):
    def __init__(self, master, on_rgb = lambda:(), on_color_mask = lambda:(), on_contours = lambda:(), on_diff = lambda:()):
        super().__init__(master=master, controlPackSide=TOP, img_size=36, btn_size=56)

        self.addControl("rgb", "assets/block_rgb.png", on_rgb)
        self.addControl("color_mask", "assets/block_color_mask.png", on_color_mask)
        self.addControl("contours", "assets/block_contours.png", on_contours)
        self.addControl("diff", "assets/block_diff.png", on_diff)

    def show(self, side = BOTTOM):
        self.pack(side=side, pady=(0,10))


class ModelControlPanel(ControlPanel):
    def __init__(self, master, on_start = lambda:(), on_stop = lambda:()):
        super().__init__(master=master)
        self.addControl("start", "assets/start_capture.png", on_start)
        self.addControl("stop", "assets/stop_capture.png", on_stop)

    def show(self, side = BOTTOM):
        self.pack(side=side, pady=(0,10))