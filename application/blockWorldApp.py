from modelling.model import BlockWorldModel
from application.colorPanel import ColorCreatePanel
from application.page import DetectionPage, TabPageContainer, ModelPage
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

from application.style import Style
from application.sideMenu import *
from application.appSettings import Settings
from detection.imageSource import Camera, ImageFile


class RGBlocksWorldApplication(Tk):
    def __init__ (self, detector, solver):
        super().__init__()
        self.title("RGBlocks World")
        self.geometry("900x680")
        self.minsize(900, 680)

        self.currentModel = None

        self.sideContainer = Frame(background=Style.back_color)
        self.sideContainer.pack(side=LEFT, fill=Y)

        self.centerContainer = Frame(background=Style.back_color)
        self.centerContainer.pack(side=RIGHT, fill=BOTH, expand=True)

        self.om = OptionsMenu(self.sideContainer)
        self.sm = SettingsMenu(self.sideContainer,"")

        self.om.addOption(self.toggleSettingsMenu, image = "assets/menu.png", activate_on_select=False)
        self.om.addOption(self.showActions, image = "assets/flash.png", set_active=True)
        self.om.addOption(self.showFilters, image = "assets/image.png") 
        self.om.addOption(self.showColors, image = "assets/colors.png")
        self.om.addOption(self.showBlockProperties, image = "assets/block.png")
        self.om.addOption(self.showDetectionParams, image = "assets/magnifier.png")
        self.om.addOption(self.showModelOptions, image = "assets/model.png")
        self.om.show(side=LEFT)

        self.sm.show(side=LEFT)

        self.pageContainer = TabPageContainer(self.centerContainer)

        self.detPage = DetectionPage(self, self.pageContainer, detector)
        self.modelPage = ModelPage(self, self.pageContainer, solver)

        self.pageContainer.addPage(self.modelPage, False)
        self.pageContainer.addPage(self.detPage, True)      
        self.pageContainer.show()

    def getModel(self):
        return self.currentModel

    def setModel(self, model):
        self.currentModel = model

    def toggleSettingsMenu(self):
        self.sm.toggle()

    def showMessage(self, message):
        messagebox.showinfo("RGBlocks World", message=message)

    def showActions(self):
        actions = [
            ("Cattura da Camera", self.startCameraDetection),
            ("Carica Immagine", self.startFileDetection),
        ]
        self.sm.clearItems()
        self.sm.setTitle("Azioni")
        self.sm.addActions(actions, TOP)

        actions = [
            ("Salva Impostazioni", self.saveSettings),
            ("Salva Impostazioni come...", lambda: self.saveSettings(use_default = False)),
            ("Carica Impostazioni", self.loadSettings)
        ]
        self.sm.addActions(actions, BOTTOM)

    def showFilters(self):
        self.sm.clearItems()
        self.sm.setTitle("Filtri Immagine")
        self.sm.addProperties(Settings.getPropertiesByGroup("image_filtering"))

    def showColors(self):
        self.sm.clearItems()
        self.sm.setTitle("Colori")
        for color in Settings.COLORS:
            self.showColor(color)
        self.sm.addAction("Aggiungi", self.createColor, BOTTOM)

    def showColor(self, color):
        self.sm.addAction(color.color_id, lambda: self.modifyColor(color), side=TOP)

    def showBlockProperties(self):
        self.sm.clearItems()
        self.sm.setTitle("Proprietà Blocchi")
        self.sm.addProperties(Settings.getPropertiesByGroup("block_properties"))

    def showDetectionParams(self):
        self.sm.clearItems()
        self.sm.setTitle("Parametri di \nRiconoscimento")
        self.sm.addProperties(Settings.getPropertiesByGroup("detection_params"))

    def showModelOptions(self):
        self.sm.clearItems()
        self.sm.setTitle("Modello")
        self.sm.addProperties(Settings.getPropertiesByGroup("model_properties"))
        self.sm.addAction("Salva Modello", self.saveModel, BOTTOM)
        self.sm.addAction("Carica Modello", self.loadModel, BOTTOM)

    def loadSettings(self):
        filename = filedialog.askopenfilename(title="Carica Impostazioni", filetypes=(("JSON", "*.json"),))
        if filename:
            Settings.loadFromFile(filename)

    def saveSettings(self, use_default = True):
        if use_default:
            filename = Settings.DEFAULT_PATH
        else:
            filename = filedialog.asksaveasfilename(defaultextension=".json", title="Salva Impostazioni", filetypes=(("JSON", "*.json"),))
        if filename:
            try:
                Settings.save(filename)
                messagebox.showinfo("RGBlocks World", message="Impostazioni salvate con successo")
            except:
                messagebox.showerror("RGBlocks World", message="Errore di salvataggio")

    def startCameraDetection(self):
        if self.pageContainer.activePage != self.detPage.id:
            self.pageContainer.openPage(self.detPage.id)
        self.detPage.stopDetection()
        self.detPage.useImageSource(Camera(init_camera=False))
        self.detPage.startDetection(setButtonActive=True)

    def startFileDetection(self):
        self.detPage.suspendDetection(setButtonActive=True)
        filename = filedialog.askopenfilename(title="Carica Immagine")
        if filename:
            if self.pageContainer.activePage != self.detPage.id:
                self.pageContainer.openPage(self.detPage.id)
            self.detPage.stopDetection()
            self.detPage.useImageSource(ImageFile(filename, initialize=False))
            self.detPage.startDetection(setButtonActive=True)
        else:
            self.detPage.restartDetection(setButtonActive=True)

    def modifyColor(self, color):
        if ColorTunePanel.openPanelCounter == 0:
            colorRemoved = ColorTunePanel(self, color).show()
            if colorRemoved:
                Settings.removeColor(color)
                self.showColors()

    def createColor(self):
        success, newColor = ColorCreatePanel(self).show()
        if success:
            Settings.addColor(newColor)
            self.sm.addAction(newColor.color_id, lambda: self.modifyColor(newColor), side=TOP)

    def loadModel(self):
        filename = filedialog.askopenfilename(title="Carica Modello", filetypes=(("JSON", "*.json"),))
        if filename:
            try:
                model = BlockWorldModel.loadFromFile(filename)
                self.currentModel = model
                if not self.pageContainer.isOpen(self.modelPage.id):
                    self.pageContainer.openPage(self.modelPage.id)
                else:
                    self.modelPage.updateModel()
            except :
                self.showMessage("ERRORE: Impossibile completare il caricamento del modello.")

    def saveModel(self):
        if self.currentModel != None:
            filename = filedialog.asksaveasfilename(defaultextension=".json", title="Salva Modello", filetypes=(("JSON", "*.json"),))
            if filename:
                try:
                    BlockWorldModel.saveModel(self.currentModel, filename)
                    self.showMessage("Modello salvato con successo")
                except:
                    self.showMessage("ERRORE: Impossibile salvare il modello corrente")

    def on_closing(self):
        if self.detPage.isDetecting():
            self.detPage.stopDetection()

        if self.modelPage.isSolving():
            self.modelPage.stopSolving()

        self.destroy()

    def show(self):
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())
        self.mainloop()