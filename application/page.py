from application.modelTunePanel import ModelTunePanel
from utils.modelPainter import ModelPainter
from modelling.problem import ColorBasedBlockWorldProblem, BlockWorldProblem
from application.appSettings import Settings
from tkinter import Frame, Button, Label, Toplevel
from tkinter.constants import BOTH, TOP, RIGHT, LEFT, BOTTOM, X
from application.style import Style
from application.imageFrame import ImageFrame
from application.controlPanel import DetectionControlPanel, DetectionViewModePanel, ModelControlPanel
from PIL import ImageTk, Image

class Page(Frame):
    def __init__(self, container, id = None, name = "", enabled = True):
        super().__init__(master=container)
        self.configure(background=Style.back_color)
        
        self.id = id if id != None else name
        self.name = name
        self.enabled = enabled

    def onEnter(self):
        pass

    def onExit(self):
        pass

    def onDestroy(self):
        pass

    def onEnable(self):
        pass

    def onDisable(self):
        pass

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.onEnable()

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.onDisable()

    def show(self):
        self.onEnter()
        self.pack(side=TOP, fill=BOTH, expand=True)

    def exit(self):
        self.onExit()
        self.pack_forget()

    def destroy(self) -> None:
        self.onDestroy()
        return super().destroy()


class TabPageContainer(Frame):
    def __init__(self, container):
        super().__init__(master=container, background=Style.back_color)

        self.font = (Style.main_font_family, Style.font_size_M)

        self.tabPanel = Frame(self, background=Style.back_color_light)
        self.tabPanel.pack(side = TOP, fill=X)

        self.pages = {}
        self.activePage = None

    def addPage(self, page, set_active = False):
        tab = Button(self.tabPanel, text=page.name, font=self.font, 
                    foreground=Style.text_color, activeforeground=Style.text_color,
                    activebackground=Style.back_color_lighter,
                    border=0, command=lambda: self.openPage(page.id), padx=20, pady=15)
        self.pages[page.id] = (tab, page)

        if set_active:
            self.openPage(page.id)
        else:
            tab.configure(background = Style.back_color_lighter)

        tab.pack(side=RIGHT)

    def openPage(self, pageID):
        if pageID in self.pages and not self.isOpen(pageID):
            if self.activePage != None:
                oldTab, oldPage = self.pages[self.activePage]
                oldTab.configure(background = Style.back_color_lighter)
                oldPage.exit()

            self.activePage = pageID
            newTab, newPage = self.pages[self.activePage]
            newTab.configure(background = Style.back_color)
            newPage.show()

    def isOpen(self, pageID):
        return self.activePage == pageID

    def show(self):
        self.openPage(self.activePage)
        self.pack(side=TOP, fill=BOTH, expand=True)


class DetectionPage(Page):

    RGB_VIEW_MODE = 0
    COLOR_MASK_VIEW_MODE = 1
    CONTOURS_VIEW_MODE = 2
    DIFF_VIEW_MODE = 3

    DETECTION_ON = 1
    DETECTION_OFF = -1
    DETECTION_SUSPENDED = 0

    def __init__(self, main, page_container, block_detector):
        super().__init__(container=page_container, id="detection_page", name="Riconoscimento", enabled=False) 

        self.detectionState = DetectionPage.DETECTION_OFF
        self.viewMode = DetectionPage.RGB_VIEW_MODE

        self.main = main
        self.blockDetector = block_detector

        self.detectionFrame = ImageFrame(self)
        self.detectionControlPanel = DetectionControlPanel(self, on_start = self.startDetection, 
                                                                 on_pause = self.suspendDetection, 
                                                                 on_stop = self.stopDetection)

        self.viewModeControlPanel = DetectionViewModePanel(self,
            lambda: self.setViewMode(DetectionPage.RGB_VIEW_MODE),
            lambda: self.setViewMode(DetectionPage.COLOR_MASK_VIEW_MODE),
            lambda: self.setViewMode(DetectionPage.CONTOURS_VIEW_MODE),
            lambda: self.setViewMode(DetectionPage.DIFF_VIEW_MODE)
        )
        self.viewModeControlPanel.setActive("rgb")

        self.viewModeControlPanel.pack(side=RIGHT, padx=(0,10))
        self.detectionFrame.pack(side=TOP, fill=BOTH, expand=True, padx=20, pady=(30,30))
        self.detectionControlPanel.pack(side=BOTTOM, pady=(0,10))

    def setViewMode(self, viewMode):
        self.viewMode = viewMode

    def onEnable(self):
        self.detectionControlPanel.enablePanel()
        self.viewModeControlPanel.enablePanel()

    def onDisable(self):
        self.detectionControlPanel.disablePanel()
        self.viewModeControlPanel.disablePanel()

    def onEnter(self):
        if self.detectionState == DetectionPage.DETECTION_ON:
            self.detectionControlPanel.setActive("start")
        elif self.detectionState == DetectionPage.DETECTION_OFF :
            self.detectionControlPanel.setActive("stop")
        elif self.detectionState == DetectionPage.DETECTION_SUSPENDED :
            self.detectionControlPanel.setActive("pause")

    def onExit(self):
        self.suspendDetection()

    def onDestroy(self):
        self.stopDetection()

    def useImageSource(self, imageSource):
        self.blockDetector.setImageSource(imageSource)

    def isDetecting(self):
        return self.detectionState == DetectionPage.DETECTION_ON

    def startDetection(self, setButtonActive = False):
        if self.detectionState == DetectionPage.DETECTION_SUSPENDED:
            self.restartDetection(setButtonActive)
        elif self.detectionState == DetectionPage.DETECTION_OFF:
            self.blockDetector.start()
            self.main.after(1, self.onDetecting)
            self.detectionState = DetectionPage.DETECTION_ON
            self.enable()
            if setButtonActive:
                self.detectionControlPanel.setActive("start")
    
    def stopDetection(self, setButtonActive = False):
        if self.detectionState != DetectionPage.DETECTION_OFF:
            self.blockDetector.stop()
            self.detectionState = DetectionPage.DETECTION_OFF
            self.clearDetection()
            self.disable()
            self.main.setModel([])
            if setButtonActive:
                self.detectionControlPanel.setActive("stop")
    
    def suspendDetection(self, setButtonActive = False):
        if self.detectionState == DetectionPage.DETECTION_ON:
            self.blockDetector.stop(releaseImageSource=False)
            self.viewModeControlPanel.disablePanel()
            self.detectionState = DetectionPage.DETECTION_SUSPENDED
            if setButtonActive:
                self.detectionControlPanel.setActive("pause")

    def restartDetection(self, setButtonActive = False):
        if self.detectionState == DetectionPage.DETECTION_SUSPENDED:
            self.blockDetector.start()
            self.main.after(1, self.onDetecting)
            self.detectionState = DetectionPage.DETECTION_ON
            self.viewModeControlPanel.enablePanel()
            if setButtonActive:
                self.detectionControlPanel.setActive("start")

    def handleDetectionError(self, errorMessage):
        self.main.showMessage(errorMessage)
        self.stopDetection(setButtonActive=True)

    def onDetecting(self):
        if self.detectionState == DetectionPage.DETECTION_ON:
            self.blockDetector.use(settings=Settings.propValues(), colors=Settings.COLORS)
            message = self.blockDetector.get(False)
            if message != None:
                if "error" in message:
                    self.handleDetectionError(errorMessage=message["error"])
                    return
                else:
                    self.main.setModel(message["model"])
                    self.showDetectionResult(message)

            self.after(1, self.onDetecting)

    def showDetectionResult(self, detectionResult):
        if self.viewMode == DetectionPage.RGB_VIEW_MODE:
            self.detectionFrame.showImageFromArray(detectionResult["frame"], target_shape=(640, 480))
        elif self.viewMode == DetectionPage.COLOR_MASK_VIEW_MODE:
            self.detectionFrame.showImageFromArray(detectionResult["mask"], target_shape=(640, 480))
        elif self.viewMode == DetectionPage.CONTOURS_VIEW_MODE:
            self.detectionFrame.showImageFromArray(detectionResult["contours"], target_shape=(640, 480))
        elif self.viewMode == DetectionPage.DIFF_VIEW_MODE:
            self.detectionFrame.showImageFromArray(detectionResult["sub"], target_shape=(640, 480))
                    
    def clearDetection(self):
        self.detectionFrame.clearFrame()


class ModelPage(Page):
        def __init__(self, main, page_container, solver):
            super().__init__(page_container, id="model_page", name="Modello", enabled=False)

            self.main = main
            self.solver = solver
            self.solver.setCallback(self.on_solved)
            self.modelPainter = ModelPainter(background=(30,30,30), foreground=(30,30,30), 
                                             font_scale=0.5, text_thickness=1)
            self.model = []
            self.solving = False
            self.solution = []
            self.currentSolutionIndex = 0

            self.infoLabel = Label(self, text = "Modello", background=Style.back_color, foreground=Style.text_color, font=(Style.main_font_family, Style.font_size_L))
            self.modelFrame = ImageFrame(self)
            self.solCounterLabel = Label(self, text = "", background=Style.back_color, foreground=Style.text_color, font=(Style.main_font_family, Style.font_size_L))
            self.modelControlPanel = ModelControlPanel(self, self.startSolving, self.stopSolving)
            self.modelControlPanel.setActive("stop")

            leftSolutionControlPanel = Frame(self, background=Style.back_color, border=0)
            self.leftSolutionControl = self.createLeftSolutionControl(leftSolutionControlPanel)
            leftSolutionControlPanel.pack(side=LEFT, fill=X, padx=(10,0))

            rightSolutionControlPanel = Frame(self, background=Style.back_color, border=0)
            self.rightSolutionControl = self.createRightSolutionControl(rightSolutionControlPanel)
            rightSolutionControlPanel.pack(side=RIGHT, fill=X, padx=(0,10))

            self.infoLabel.pack(side=TOP, pady=(40,0))
            self.modelFrame.pack(side=TOP, fill=BOTH, expand=True, padx=20, pady=(10,10))
            self.modelControlPanel.pack(side=BOTTOM, pady=(0,10))


        def onEnable(self):
            self.modelControlPanel.enablePanel()

        def onDisable(self):
            self.modelControlPanel.disablePanel()

        def onEnter(self):
            self.model = self.main.getModel()
            if self.model != None and len(self.model) > 0:
                self.modelPainter.highlightBlock(False)
                self.showModel(self.model)
                self.enable()
                self.showInfo("Modello")
                self.resetSolution()
            else:
                self.modelControlPanel.setActive("stop")
                self.clearModel()
                self.disable()
                if len(self.solution) > 0:
                    self.currentSolutionIndex = 0
                    self.modelPainter.highlightBlock(False)
                    self.showModel(self.solution[0].state[0])
                    self.showInfo("Stato Iniziale")
                    self.showSolutionStepCounter(update=True)
                    self.showSolutionControls()

        def onExit(self):
            self.stopSolving()

        def updateModel(self):
            self.model = self.main.getModel()
            if self.model != None and len(self.model) > 0:
                self.showModel(self.model)
                self.enable()
                self.showInfo("Modello")
                self.resetSolution()

        def showModel(self, model):
            if model != None and len(model) > 0:
                self.modelPainter.setModel(model)
                self.modelFrame.showImageFromArray(self.modelPainter.paint())

        def showInfo(self, info):
            self.infoLabel.configure(text=info)

        def showSolutionStepCounter(self, update = False):
            if self.solCounterLabel.winfo_exists() and not self.solCounterLabel.winfo_ismapped():
                self.solCounterLabel.pack(side=TOP, pady=(0,40))
            if update:
                self.updateSolutionStepCounter()

        def hideSolutionStepCounter(self):
            if self.solCounterLabel.winfo_exists():
                self.solCounterLabel.pack_forget()

        def updateSolutionStepCounter(self):
            if self.solution != None:
                self.solCounterLabel.configure(
                    text= str(self.currentSolutionIndex + 1) + " - " + str(len(self.solution))
                )

        def createLeftSolutionControl(self, container):
            img = Image.open("assets/arrow_left.png")
            img = img.resize((20, 20), Image.ANTIALIAS)
            tmp = ImageTk.PhotoImage(img)

            control = Button(container, border=0, image=tmp, width=40, height=40)
            control.image = tmp
            control.configure(command = self.showPrevSolutionStep,
                              background = Style.back_color, activebackground=Style.back_color)
            return control

        def createRightSolutionControl(self, container):
            img = Image.open("assets/arrow_right.png")
            img = img.resize((20, 20), Image.ANTIALIAS)
            tmp = ImageTk.PhotoImage(img)

            control = Button(container, border=0, image=tmp, width=40, height=40)
            control.image = tmp
            control.configure(command = self.showNextSolutionStep,
                              background = Style.back_color, activebackground=Style.back_color)
            return control

        def showLeftSolutionControl(self):
            if self.leftSolutionControl.winfo_exists() and not self.leftSolutionControl.winfo_ismapped():
                self.leftSolutionControl.pack()

        def showRightSolutionControl(self):
            if self.rightSolutionControl.winfo_exists() and not self.rightSolutionControl.winfo_ismapped():
                self.rightSolutionControl.pack()

        def hideLeftSolutionControl(self):
            if self.leftSolutionControl.winfo_exists():
                self.leftSolutionControl.pack_forget()

        def hideRightSolutionControl(self):
            if self.rightSolutionControl.winfo_exists():
                self.rightSolutionControl.pack_forget()

        def showSolutionControls(self):
            if self.currentSolutionIndex < len(self.solution) - 1:
                self.showRightSolutionControl()               
            if self.currentSolutionIndex > 0:
                self.showLeftSolutionControl()

        def resetSolution(self):
            self.solution = []
            self.currentSolutionIndex = 0
            self.hideSolutionStepCounter()
            self.hideLeftSolutionControl()
            self.hideRightSolutionControl()

        def showNextSolutionStep(self):
            if self.currentSolutionIndex < len(self.solution) - 1:
                self.currentSolutionIndex += 1
                state = self.solution[self.currentSolutionIndex].state
                if state[1] != None:
                    # se in questo stato il robot ha un blocco in mano
                    # evidenzio quel blocco e mostro il modello dello stato precedente
                    self.modelPainter.highlightBlock(True, state[1].id)
                    self.showModel(self.solution[self.currentSolutionIndex - 1].state[0])
                else :
                    # altrimenti mostro semplicemente il nuovo stato 
                    self.modelPainter.highlightBlock(False)
                    self.showModel(self.solution[self.currentSolutionIndex].state[0])

                if self.currentSolutionIndex == len(self.solution) - 1:
                    self.hideRightSolutionControl()
                elif self.currentSolutionIndex == 1:
                    self.showLeftSolutionControl()
                
                self.showInfo(str(self.solution[self.currentSolutionIndex].action))
                self.updateSolutionStepCounter()

        def showPrevSolutionStep(self):
            if self.currentSolutionIndex > 0:
                self.currentSolutionIndex -= 1
                state = self.solution[self.currentSolutionIndex].state
                if state[1] != None:
                    # se in questo stato il robot ha un blocco in mano
                    # evidenzio quel blocco e mostro il modello dello stato precedente
                    self.modelPainter.highlightBlock(True, state[1].id)
                    self.showModel(self.solution[self.currentSolutionIndex + 1].state[0])
                else :
                    # altrimenti mostro semplicemente il nuovo stato 
                    self.modelPainter.highlightBlock(False)
                    self.showModel(self.solution[self.currentSolutionIndex].state[0])
                if self.currentSolutionIndex == 0:
                    self.hideLeftSolutionControl()
                elif self.currentSolutionIndex == len(self.solution) - 2:
                    self.showRightSolutionControl()

                if self.currentSolutionIndex == 0:
                    self.showInfo("Stato Iniziale")
                else:
                    self.showInfo(str(self.solution[self.currentSolutionIndex].action))

                self.updateSolutionStepCounter()

        def clearModel(self):
            self.modelFrame.clearFrame()

        def isSolving(self):
            return self.solving

        def startSolving(self):
            if not self.solving:
                goalType = Settings.getPropertyByID("goal_type").value
                if goalType == "Default":
                    self.solver.setProblem(ColorBasedBlockWorldProblem(self.model))
                    self.solver.useAlgorithm(Settings.getPropertyByID("algorithm").value)
                    self.resetSolution()
                    self.solver.solve()
                    self.solving = True
                    self.showInfo("Running...")
                elif goalType == "Custom":
                    success, goal = ModelTunePanel(self, self.model).show()
                    if success:
                        self.solver.setProblem(BlockWorldProblem(self.model, goal))
                        self.solver.useAlgorithm(Settings.getPropertyByID("algorithm").value)
                        self.resetSolution()
                        self.solver.solve()
                        self.solving = True
                        self.showInfo("In Esecuzione...")
                    else:
                        self.modelControlPanel.setActive("stop")

        def stopSolving(self):
            if self.solving:
                self.showInfo("Arresto...")
                self.solver.stopSolving()

        def on_solved(self, success, result):
            if success:
                self.main.showMessage("Soluzione trovata in " + str(result["time"]) + " secondi" +
                                     "\nNodi Espansi : " + str(result["expanded"]) +
                                     "\nNodi Testati : " + str(result["tested"]))
                self.modelControlPanel.setActive("stop")
                self.solving = False
                self.solution = result["solution"]
                self.showSolutionControls()
                self.showSolutionStepCounter(update=True)
                self.showInfo("Stato Iniziale")
                return
            else:
                self.main.showMessage("Nessuna Soluzione Trovata")
                self.modelControlPanel.setActive("stop")
                self.solving = False
                self.showInfo("Modello")
        