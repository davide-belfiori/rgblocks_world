from application.appSettings import Settings
from tkinter import *
from application.style import Style

class PropertyScale(Scale):
    def __init__(self, master, property, font = (Style.main_font_family, Style.font_size_M)) -> None:
        super().__init__(master = master,  bg=Style.back_color_light, label=property.property_name, font=font, 
                        orient=HORIZONTAL, length=200,
                        from_=property.min, to=property.max, resolution=property.resolution)
        self.configure(bd=0, highlightthickness=0, foreground=Style.text_color)
        self.set(property.value)
        self.configure(command=lambda v: property.set(v))


class PropertyCheck(Frame):
    def __init__(self, master, property, font = (Style.main_font_family, Style.font_size_M)) -> None:
        super().__init__(master, bg=Style.back_color_light, border=0, borderwidth=0, padx=10, pady=10)

        self.propLabel = Label(self, text=property.property_name, font = font, fg=Style.text_color, bg=Style.back_color_light, border=0, borderwidth=0)

        self.check = Checkbutton(self, bg=Style.back_color_light, border=0, borderwidth=0)
        if property.value:
            self.check.select()
        else: self.check.deselect()
        self.check.configure(command=property.switch)

        self.check.pack(side=LEFT, padx=(0,2))
        self.propLabel.pack(side=RIGHT, fill=X, expand=True)


class PropertyOptionsMenu(Frame):
    def __init__(self, master, property, font = (Style.main_font_family, Style.font_size_M)) -> None:
        super().__init__(master, bg=Style.back_color_light, border=0, borderwidth=0, padx=0, pady=10)

        propLabel = Label(self, text=property.property_name, 
                          font = font, 
                          fg=Style.text_color, bg=Style.back_color_light, 
                          border=0, borderwidth=0)

        solverVariable = StringVar(self)
        solverVariable.set(property.value)
        optMenu = OptionMenu(self, solverVariable, *(property.options),
                             command = property.set)
        optMenu.configure(background=Style.back_color_lighter, foreground=Style.text_color,
                        font=(Style.main_font_family, Style.font_size_M), 
                        activebackground= Style.back_color_lighter, activeforeground=Style.text_color,
                        border=0, highlightthickness=0, pady=10, width=22)

        propLabel.pack(side=TOP, pady=(0,10))
        optMenu.pack(side=BOTTOM)