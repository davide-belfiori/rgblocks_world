from tkinter import *
from application.style import Style
from PIL import Image
import PIL.ImageTk as itk
from application.controlPanel import *

class ImageFrame(Frame):
    def __init__(self, container):
        super().__init__(master=container, background=Style.back_color)
        self.configure(highlightthickness=0, highlightbackground="white")

        self.canvas = Canvas(self, background=Style.back_color_light, highlightthickness=0)
        self.canvas.pack(side=TOP,expand=True)

    def showImageFromFile(self, filename):
        self.img = PhotoImage(file=filename)
        self.canvas.configure(height=self.img.height(), width=self.img.width())
        self.canvas.create_image(0,0,image=self.img,anchor=NW)

    def showImageFromArray(self, array, target_shape = None):
        image = Image.fromarray(array)
        if target_shape != None:
            image = image.resize(target_shape, Image.ANTIALIAS)
        self.img = itk.PhotoImage(image = image)
        self.canvas.configure(height=self.img.height(), width=self.img.width())
        self.canvas.create_image(0,0,image=self.img,anchor=NW)

    def clearFrame(self):
        self.canvas.delete("all")

    def show(self):
        self.pack(side=TOP, fill=BOTH, expand=True)
        
