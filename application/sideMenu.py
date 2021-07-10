from application.colorPanel import ColorTunePanel
from tkinter import *
from tkinter.font import Font
from application.style import Style
from application.propertyWidget import *
from application.appSettings import Property

from PIL import ImageTk, Image


class SettingsMenu(Frame):
    def __init__(self, container, title = "Side Menu"):
        super().__init__(master=container, background=Style.back_color_light, pady=5, padx=5)

        self.hidden = True

        self.titleFont = (Style.main_font_family, Style.font_size_L)
        self.settFont = (Style.main_font_family, Style.font_size_M)

        self.menuTitle = Label(self, text=title, font=self.titleFont, 
                               background=Style.back_color_light, foreground=Style.text_color, 
                               border=0)
        self.menuTitle.pack(side=TOP, fill=X, pady=15)

        self.propertiesFrame = Frame(self, background=Style.back_color_light, border=0, padx=20)
        self.propertiesFrame.pack(side=TOP, fill=BOTH, expand=True)

        self.actionsFrame = Frame(self, background=Style.back_color_light, border=0, padx=10)
        self.actionsFrame.pack(side=BOTTOM, fill=X)

    def addItem(self, item, side):
        if side == TOP:
            item.pack(side=side, fill=X, pady=(20,0))
        elif side == BOTTOM:
            item.pack(side=side, fill=X, pady=(0,10))

    def clearItems(self):
        for c in self.propertiesFrame.winfo_children():
                c.destroy()

    def addProperty(self, property):
        if isinstance(property, Property):
            if property.type == Property.TYPE_FLOAT_RANGE or property.type == Property.TYPE_INT_RANGE:
                self.addItem(PropertyScale(self.propertiesFrame, property), TOP)
            elif property.type == Property.TYPE_BOOL:
                self.addItem(PropertyCheck(self.propertiesFrame, property), TOP)
            elif property.type == Property.TYPE_MULTIPLE_OPTIONS:
                self.addItem(PropertyOptionsMenu(self.propertiesFrame, property), TOP)

    def addProperties(self, properties):
        for property in properties:
            self.addProperty(property)

    def addAction(self, name, command, side):
        self.addItem(Button(self.propertiesFrame, text=name, font=self.settFont, foreground=Style.text_color, pady=5,
                        background=Style.button_color, activebackground=Style.button_color_active,
                        border=0, width=20, 
                        command = command), side)

    def addActions(self, actions, side):
        for (name, command) in actions:
            self.addAction(name, command, side)

    def addColorAction(self, color, side):
        self.addAction(color.color_id, lambda:ColorTunePanel(self.master, color), side)
    
    def setTitle(self, title=""):
        if title != None:
            self.menuTitle.configure(text=title)

    def toggle(self):
        if self.hidden:
            self.show(self.side)
        else:
            self.pack_forget()
            self.hidden = True

    def show(self, side):
        self.hidden = False
        self.side = side
        self.pack(side=side, fill=Y)


class OptionsMenu(Frame):
    def __init__(self, container):
        super().__init__(master=container, background=Style.back_color_lighter)
        self.font = Font(self, family=Style.main_font_family, size=Style.font_size_XL)
        self.configure(width=50)
        self.activeOption = None

    def addOption(self, command, image, set_active = False, activate_on_select = True):

        img = Image.open(image)
        img = img.resize((30, 30), Image.ANTIALIAS)
        tmp = ImageTk.PhotoImage(img)

        option = Button(self, pady=30, padx=30,
                        border=0, image=tmp, width=60, height=60)
        option.image = tmp
        option.configure(command = lambda: self.on_option_selected(option, command, activate_on_select))

        if set_active:
            option.configure(background = Style.back_color_light)
            self.activeOption = option
            command()
        else:
            option.configure(background = Style.back_color_lighter)

        option.pack(side=TOP, fill=X)
    
    def on_option_selected(self, option, command, activate_on_select):
        if activate_on_select:
            if self.activeOption != None:
                self.activeOption.configure(background=Style.back_color_lighter)
            
            option.configure(background = Style.back_color_light)
            self.activeOption = option
        command() 

    def show(self, side):
        self.pack(side=side, fill=Y)
