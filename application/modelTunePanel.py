from modelling.utils import mode
from modelling.model import BlockWorldModel
from tkinter import *
from utils.modelPainter import ModelPainter
from application.style import Style
from application.imageFrame import ImageFrame
from PIL import ImageTk, Image

class ModelTunePanel(Toplevel):
       def __init__ (self, master, initModel = []):
              super().__init__(master=master, background=Style.back_color_light)
              self.minsize(width=600, height=600)
              self.resizable(False, False)
              self.success = False

              self.model = BlockWorldModel.asList(initModel)
              self.modelPainter = ModelPainter(background=(30,30,30), foreground=(30,30,30), 
                                          font_scale=0.55, text_thickness=1, 
                                          border_color=(100,100,100), border_thickness=4)
              self.modelPainter.setModel(initModel)

              self.focused = None
              self.selected = False

              # calcolo l'indice del primo stack non vuoto
              stack_index = None
              if self.model != None and len(self.model) > 0:
                     for i,s in enumerate(self.model):
                            if len(s) > 0:
                                   stack_index = i
                                   break
              if stack_index != None:
                     self.focused = [stack_index, len(self.model[stack_index]) - 1]
                     self.modelPainter.focusBlock(True, self.model[stack_index][-1].id)

              self.imFrame = ImageFrame(self)
              self.imFrame.showImageFromArray(self.modelPainter.paint())

              self.commandFrame = Frame(self, background=Style.back_color_light)

              shuffleImg = Image.open("assets/shuffle.png")
              shuffleImg = shuffleImg.resize((30, 30), Image.ANTIALIAS)
              shuffleTmp = ImageTk.PhotoImage(shuffleImg)
              shuffle = Button(self.commandFrame, border=0, image=shuffleTmp, width=30, height=30)
              shuffle.image = shuffleTmp
              shuffle.configure(command = self.shuffle)
              shuffle.configure(background = Style.back_color_light, activebackground=Style.back_color_lighter)
              shuffle.pack(side=LEFT, padx=(0,60))

              Button(self.commandFrame, text="Seleziona", 
                     background=Style.button_color, foreground=Style.text_color,
                     activebackground=Style.button_color_active, activeforeground=Style.text_color,
                     border=0, command=self.selectBlock,
                     padx=20, pady=10).pack(side=LEFT)

              self.blockControlFrame = Frame(self.commandFrame, background=Style.back_color_light)
              
              arrowUpimg = Image.open("assets/arrow_up.png")
              arrowUpimg = arrowUpimg.resize((30, 30), Image.ANTIALIAS)
              arrowUptmp = ImageTk.PhotoImage(arrowUpimg)
              arrowUp = Button(self.blockControlFrame, border=0, image=arrowUptmp, width=30, height=30)
              arrowUp.image = arrowUptmp
              arrowUp.configure(command = self.onUp)
              arrowUp.configure(background = Style.back_color_light, activebackground=Style.back_color_lighter)
              arrowUp.grid(row=0, column=0, columnspan=3)

              arrowDownimg = Image.open("assets/arrow_down.png")
              arrowDownimg = arrowDownimg.resize((30, 30), Image.ANTIALIAS)
              arrowDowntmp = ImageTk.PhotoImage(arrowDownimg)
              arrowDown = Button(self.blockControlFrame, border=0, image=arrowDowntmp, width=30, height=30)
              arrowDown.image = arrowDowntmp
              arrowDown.configure(command = self.onDown)
              arrowDown.configure(background = Style.back_color_light, activebackground=Style.back_color_lighter)
              arrowDown.grid(row=2, column=0, columnspan=3)

              arrowLeftimg = Image.open("assets/arrow_left.png")
              arrowLeftimg = arrowLeftimg.resize((30, 30), Image.ANTIALIAS)
              arrowLefttmp = ImageTk.PhotoImage(arrowLeftimg)
              arrowLeft = Button(self.blockControlFrame, border=0, image=arrowLefttmp, width=30, height=30)
              arrowLeft.image = arrowLefttmp
              arrowLeft.configure(command = self.onLeft)
              arrowLeft.configure(background = Style.back_color_light, activebackground=Style.back_color_lighter)
              arrowLeft.grid(row=1, column=0)

              arrowRightimg = Image.open("assets/arrow_right.png")
              arrowRightimg = arrowRightimg.resize((30, 30), Image.ANTIALIAS)
              arrowRighttmp = ImageTk.PhotoImage(arrowRightimg)
              arrowRight = Button(self.blockControlFrame, border=0, image=arrowRighttmp, width=30, height=30)
              arrowRight.image = arrowRighttmp
              arrowRight.configure(command = self.onRight)
              arrowRight.configure(background = Style.back_color_light, activebackground=Style.back_color_lighter)
              arrowRight.grid(row=1, column=2)

              self.blockControlFrame.pack(side=LEFT, padx=20)

              blankimg = Image.open("assets/blank.png")
              blankimg = blankimg.resize((30, 30), Image.ANTIALIAS)
              blanktmp = ImageTk.PhotoImage(blankimg)
              blank = Label(self.blockControlFrame, border=0, image=blanktmp, width=30, height=30)
              blank.image = blanktmp
              blank.configure(background = Style.back_color_light)
              blank.grid(row=1, column=1)

              Button(self.commandFrame, text="Rilascia", 
                     background=Style.button_color, foreground=Style.text_color,
                     activebackground=Style.button_color_active, activeforeground=Style.text_color,
                     border=0, command = self.releaseBlock,
                     padx=20, pady=10).pack(side=LEFT)

              doneImg = Image.open("assets/check.png")
              doneImg = doneImg.resize((30, 30), Image.ANTIALIAS)
              doneTmp = ImageTk.PhotoImage(doneImg)
              done = Button(self.commandFrame, border=0, image=doneTmp, width=30, height=30)
              done.image = doneTmp
              done.configure(command = self.ok)
              done.configure(background = Style.back_color_light, activebackground=Style.back_color_lighter)
              done.pack(side=LEFT, padx=(60,0))

              self.commandFrame.pack(side=BOTTOM, padx=10, pady=10)
              self.imFrame.pack(side=TOP, fill=BOTH, expand=True, padx=20, pady=20)

              self.bind("<Left>", lambda e : self.onLeft())
              self.bind("<Right>", lambda e : self.onRight())
              self.bind("<Up>", lambda e : self.onUp())
              self.bind("<Down>", lambda e : self.onDown())
              self.bind("<Return>", lambda e : self.onReturn())

       def updateFigure(self):
              self.modelPainter.setModel(self.model)
              if self.selected:
                     self.modelPainter.highlightBlock(True, self.model[self.focused[0]][self.focused[1]].id)
              else :
                     self.modelPainter.highlightBlock(False)
                     if self.focused != None:
                            self.modelPainter.focusBlock(True, self.model[self.focused[0]][self.focused[1]].id)
                     else:
                            self.modelPainter.focusBlock(False)

              self.imFrame.showImageFromArray(self.modelPainter.paint())  

       def selectBlock(self):
              if not self.selected:
                     self.selected = True
                     self.updateFigure()

       def releaseBlock(self):
              if self.selected:
                     self.selected = False
                     self.updateFigure()

       def onReturn(self):
              if not self.selected:
                     self.selected = True
                     self.updateFigure()
              else:
                     self.selected = False
                     self.updateFigure()

       def onUp(self):
              if not self.selected:
                     if self.focused != None:
                            self.focused[1] = min(len(self.model[self.focused[0]]) - 1, self.focused[1] + 1)
              else:
                     if self.focused[1] < len(self.model[self.focused[0]]) - 1:
                            tmp = self.model[self.focused[0]][self.focused[1]]
                            self.model[self.focused[0]][self.focused[1]] = self.model[self.focused[0]][self.focused[1] + 1]
                            self.model[self.focused[0]][self.focused[1] + 1] = tmp
                            self.focused[1] += 1
              self.updateFigure()

       def onDown(self):
              if not self.selected:
                     if self.focused != None:
                            self.focused[1] = max(0, self.focused[1] - 1)
              else:
                     if self.focused[1] > 0:
                            tmp = self.model[self.focused[0]][self.focused[1]]
                            self.model[self.focused[0]][self.focused[1]] = self.model[self.focused[0]][self.focused[1] - 1]
                            self.model[self.focused[0]][self.focused[1] - 1] = tmp
                            self.focused[1] -= 1
              self.updateFigure()

       def onRight(self):
              if not self.selected:
                     if self.focused != None:
                            oldStack = self.focused[0]
                            nextStack = self.focused[0] + 1
                            while nextStack < len(self.model):
                                   if len(self.model[nextStack]) > 0:
                                          self.focused[0] = nextStack
                                          break
                                   nextStack += 1

                            currentBlockIdx = self.focused[1]
                            nextBlock = min(len(self.model[self.focused[0]]) - 1, currentBlockIdx)
                            self.focused[1] = nextBlock
              else:
                     if self.focused[0] < len(self.model) - 1:
                            oldStack = self.focused[0]
                            nextStack = self.focused[0] + 1
                            currentBlockIdx = self.focused[1]

                            toMove = self.model[oldStack][currentBlockIdx]
                            self.model[oldStack].remove(toMove)
                            self.model[nextStack].append(toMove)

                            self.focused = [nextStack, len( self.model[nextStack]) - 1]
              self.updateFigure()
                     
       def onLeft(self):
              if not self.selected:
                     if self.focused != None:
                            oldStack = self.focused[0]
                            prevStack = self.focused[0] - 1
                            while prevStack >= 0:
                                   if len(self.model[prevStack]) > 0:
                                          self.focused[0] = prevStack
                                          break
                                   prevStack -= 1

                            currentBlockIdx = self.focused[1]
                            nextBlock = min(len(self.model[self.focused[0]]) - 1, currentBlockIdx)
                            self.focused[1] = nextBlock
              else:
                     if self.focused[0] > 0:
                            oldStack = self.focused[0]
                            nextStack = self.focused[0] - 1
                            currentBlockIdx = self.focused[1]

                            toMove = self.model[oldStack][currentBlockIdx]
                            self.model[oldStack].remove(toMove)
                            self.model[nextStack].append(toMove)

                            self.focused = [nextStack, len( self.model[nextStack]) - 1]
              self.updateFigure()

       def shuffle(self):
              self.model = BlockWorldModel.shuffle(self.model)
              
              self.selected = False

              # calcolo l'indice del primo stack non vuoto
              stack_index = None
              if self.model != None and len(self.model) > 0:
                     for i,s in enumerate(self.model):
                            if len(s) > 0:
                                   stack_index = i
                                   break
              if stack_index != None:
                     self.focused = [stack_index, len(self.model[stack_index]) - 1]
                     self.modelPainter.focusBlock(True, self.model[stack_index][-1].id)

              self.updateFigure()

       def ok(self):
              self.success = True
              self.destroy()

       def close(self):
              self.success = False
              self.destroy()

       def show(self):
              self.wm_deiconify()
              self.grab_set()
              self.wait_window()
              return self.success, self.model