from application.appSettings import Color, Settings
from tkinter import *
from application.style import Style
from application.propertyWidget import PropertyScale


class ColorTunePanel(Toplevel):

        openPanelCounter = 0

        def __init__ (self, master, color):
                super().__init__(master=master, background=Style.back_color_light)
                self.minsize(width=600, height=300)
                self.resizable(False, False)
                self.color = color
                self.remove = False

                labelFrame = Frame(self, background=Style.back_color)
                Label(labelFrame, text="Color ID : " + str(self.color.color_id), font=(Style.main_font_family, Style.font_size_M),
                        background=Style.back_color, foreground=Style.text_color).pack(side=LEFT, padx=20, pady=20)
                Label(labelFrame, text="Color Group : " + str(self.color.color_group), font=(Style.main_font_family, Style.font_size_M),
                        background=Style.back_color, foreground=Style.text_color).pack(side=RIGHT, padx=20, pady=20)
                labelFrame.pack(side = TOP, fill=X)
                
                propFrame = Frame(self, background=Style.back_color_light)

                PropertyScale(propFrame, self.color.lowerH, font=(Style.main_font_family, Style.font_size_M)).grid(row=1, column=0, padx=(10,0), pady=(20,0))
                PropertyScale(propFrame, self.color.lowerS, font=(Style.main_font_family, Style.font_size_M)).grid(row=1, column=1, padx=(15,0), pady=(20,0))
                PropertyScale(propFrame, self.color.lowerV, font=(Style.main_font_family, Style.font_size_M)).grid(row=1, column=2, padx=(15,10), pady=(20,0))

                PropertyScale(propFrame, self.color.upperH, font=(Style.main_font_family, Style.font_size_M)).grid(row=2, column=0, padx=(10,0), pady=(10,0))
                PropertyScale(propFrame, self.color.upperS, font=(Style.main_font_family, Style.font_size_M)).grid(row=2, column=1, padx=(15,0), pady=(10,0))
                PropertyScale(propFrame, self.color.upperV, font=(Style.main_font_family, Style.font_size_M)).grid(row=2, column=2, padx=(15,10), pady=(10,0))

                PropertyScale(propFrame, self.color.R, font=(Style.main_font_family, Style.font_size_M)).grid(row=3, column=0, padx=(10,0), pady=(10,0))
                PropertyScale(propFrame, self.color.G, font=(Style.main_font_family, Style.font_size_M)).grid(row=3, column=1, padx=(15,0), pady=(10,0))
                PropertyScale(propFrame, self.color.B, font=(Style.main_font_family, Style.font_size_M)).grid(row=3, column=2, padx=(15,10), pady=(10,0))

                propFrame.pack(side=TOP, fill=BOTH, expand=True)

                buttonsFrame = Frame(self, background=Style.back_color_light)

                Button(buttonsFrame, text="Rimuovi", 
                        background=Style.button_color, activebackground=Style.button_color_active,
                        foreground=Style.text_color, activeforeground=Style.text_color,
                        border = 0,
                        font=(Style.main_font_family, Style.font_size_M),
                        command=self.removeColor,
                        pady=10).pack(side=RIGHT, fill=X, expand=True, padx=(10))

                buttonsFrame.pack(side=BOTTOM, fill=X, pady=(40,10))

                ColorTunePanel.openPanelCounter += 1

        def removeColor(self):
                self.remove = True
                self.destroy()

        def show(self):
                self.wm_deiconify()
                self.wait_window()
                ColorTunePanel.openPanelCounter -= 1
                return self.remove

class ColorCreatePanel(Toplevel):
        def __init__ (self, master):
                super().__init__(master=master, background=Style.back_color_light)
                self.minsize(width=600, height=300)
                self.resizable(False, False)

                self.success = False
                self.newColor = Color("", "")
                self.color_id_var = StringVar(value="color_id")
                self.color_group_var = StringVar(value="color_group")

                labelFrame = Frame(self, background=Style.back_color)

                Label(labelFrame, text="Color ID : ", font=(Style.main_font_family, Style.font_size_M),
                        background=Style.back_color, foreground=Style.text_color).pack(side=LEFT, padx=20, pady=20)
                Entry(labelFrame, textvariable=self.color_id_var,
                        background=Style.back_color, foreground=Style.text_color).pack(side=LEFT, pady=20)

                Entry(labelFrame, textvariable=self.color_group_var,
                        background=Style.back_color, foreground=Style.text_color).pack(side=RIGHT, pady=20, padx=20)
                Label(labelFrame, text="Color Group : ", font=(Style.main_font_family, Style.font_size_M),
                        background=Style.back_color, foreground=Style.text_color).pack(side=RIGHT, pady=20)

                labelFrame.pack(side = TOP, fill=X)
                
                propFrame = Frame(self, background=Style.back_color_light)

                PropertyScale(propFrame, self.newColor.lowerH, font=(Style.main_font_family, Style.font_size_M)).grid(row=1, column=0, padx=(10,0), pady=(20,0))
                PropertyScale(propFrame, self.newColor.lowerS, font=(Style.main_font_family, Style.font_size_M)).grid(row=1, column=1, padx=(15,0), pady=(20,0))
                PropertyScale(propFrame, self.newColor.lowerV, font=(Style.main_font_family, Style.font_size_M)).grid(row=1, column=2, padx=(15,10), pady=(20,0))

                PropertyScale(propFrame, self.newColor.upperH, font=(Style.main_font_family, Style.font_size_M)).grid(row=2, column=0, padx=(10,0), pady=(10,0))
                PropertyScale(propFrame, self.newColor.upperS, font=(Style.main_font_family, Style.font_size_M)).grid(row=2, column=1, padx=(15,0), pady=(10,0))
                PropertyScale(propFrame, self.newColor.upperV, font=(Style.main_font_family, Style.font_size_M)).grid(row=2, column=2, padx=(15,10), pady=(10,0))

                PropertyScale(propFrame, self.newColor.R, font=(Style.main_font_family, Style.font_size_M)).grid(row=3, column=0, padx=(10,0), pady=(10,0))
                PropertyScale(propFrame, self.newColor.G, font=(Style.main_font_family, Style.font_size_M)).grid(row=3, column=1, padx=(15,0), pady=(10,0))
                PropertyScale(propFrame, self.newColor.B, font=(Style.main_font_family, Style.font_size_M)).grid(row=3, column=2, padx=(15,10), pady=(10,0))

                propFrame.pack(side=TOP, fill=BOTH, expand=True)

                self.errorLabel = Label(self, text="", font=(Style.main_font_family, Style.font_size_M),
                                        background=Style.back_color_light, foreground=Style.text_color)

                buttonsFrame = Frame(self, background=Style.back_color_light)

                Button(buttonsFrame, text="Salva", 
                        background=Style.button_color, activebackground=Style.button_color_active,
                        foreground=Style.text_color, activeforeground=Style.text_color,
                        border = 0,
                        font=(Style.main_font_family, Style.font_size_M),
                        command=self.saveColor,
                        pady=10).pack(side=RIGHT, fill=X, expand=True, padx=(10))

                buttonsFrame.pack(side=BOTTOM, fill=X, pady=(40,10))

        def showErrorMessage(self, message):
                if self.errorLabel.winfo_exists() and not self.errorLabel.winfo_ismapped():
                                self.errorLabel.pack(side=BOTTOM, pady=(40,0))
                self.errorLabel.configure(text = message)
        
        def saveColor(self):
                colId = self.color_id_var.get()
                colGroup = self.color_group_var.get()

                if colId != "" and Settings.getColorByID(colId) == None:
                        if colGroup != "":
                                self.newColor.setId(colId)
                                self.newColor.setGroup(colGroup)
                                self.success = True
                                self.destroy()
                        else:
                                self.showErrorMessage("Gruppo Colore non valido")
                else: 
                        self.showErrorMessage("ID Colore non valido")

        def show(self):
                self.wm_deiconify()
                self.grab_set()
                self.wait_window()
                self.grab_release()
                if self.success:
                        return True, self.newColor
                return False, None


