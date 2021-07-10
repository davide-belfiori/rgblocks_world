from cv2 import cv2 as cv
import numpy as np
import functools

class ModelPainter():

    def __init__(self, model = [], background = (0,0,0), foreground = (255,255,255), 
                                   image_width = 600, image_height = 480,
                                   text_thickness = 2, font_scale = 1,
                                   border_thickness = 4, border_color = (0,0,0)):
        self.model = model
        self.background = background
        self.foreground = foreground
        self.image_width = image_width
        self.image_height = image_height
        self.text_thickness = text_thickness
        self.font_scale = font_scale
        self.border_thickness = border_thickness
        self.border_color = border_color

        self.highlight = False
        self.highlightedBlock = None
        self.focus = False
        self.focusedBlock = None

    def setModel(self, model):
        self.model = model

    def setBackground(self, background):
        self.background = background

    def setForeground(self, foreground):
        self.foreground = foreground

    def setWidth(self, width):
        self.image_width = width

    def setHeight(self, height):
        self.image_height = height

    def highlightBlock(self, highlight = False, block_id = None):
        self.highlight = highlight
        if self.highlight:
            self.highlightedBlock = block_id
        else:
            self.highlightedBlock = None

    def focusBlock(self, focus = False, block_id = None):
        self.focus = focus
        if self.focus:
            self.focusedBlock = block_id
        else:
            self.focusedBlock = None

    def base(self, width, height, alpha = 255):
        r = np.zeros(shape=(height, width), dtype=np.uint8) + self.background[0]
        g = np.zeros(shape=(height, width), dtype=np.uint8) + self.background[1]
        b = np.zeros(shape=(height, width), dtype=np.uint8) + self.background[2]
        alpha = np.zeros(shape=(height, width), dtype=np.uint8) + alpha

        return cv.merge((r,g,b,alpha))
        
    def calcBlockSize(self):
        n_stack = len(self.model)
        if n_stack == 0:
            return 0
        max_stack_len = len(functools.reduce(lambda s1, s2 : s1 if len(s1) > len(s2) else s2, self.model))
        if max_stack_len == 0:
            return 0
        max_block_width = self.image_width // n_stack
        max_block_height = self.image_height // max_stack_len

        return min(max_block_width, max_block_height)

    def paintBlock(self, base, block, point, block_size):
        bcolor = list(block.rgb())
        bcolor.append(255)
        fcolor = list(self.foreground)
        fcolor.append(255)

        if self.highlight:
            if block.id != self.highlightedBlock:
                bcolor[3] = 50
                fcolor[3] = 80

        cv.rectangle(base, (point[0] + self.border_thickness // 2, point[1] + self.border_thickness // 2), 
                     (point[0] + block_size - self.border_thickness // 2, point[1] + block_size - self.border_thickness // 2), 
                     color=bcolor, 
                     thickness= -1)
        cv.putText(base, str(block.id), 
                   (point[0] + 8, point[1] + 30), 
                   cv.FONT_HERSHEY_SIMPLEX, self.font_scale, 
                   fcolor, 
                   self.text_thickness)

        if self.focus and block.id == self.focusedBlock:
            bdcolor = list(self.border_color)
            bdcolor.append(255)
            cv.rectangle(base, (point[0] + self.border_thickness // 2, point[1] + self.border_thickness // 2), 
                        (point[0] + block_size - self.border_thickness // 2, point[1] + block_size - self.border_thickness // 2), 
                        color=bdcolor, 
                        thickness=self.border_thickness)

    def paint(self):
        base = self.base(self.image_width, self.image_height)
        block_size = self.calcBlockSize()

        for i,stack in enumerate(self.model):
            x_coord = block_size * i           
            for j,block in enumerate(stack):
                y_coord = self.image_height - block_size * (j+1)
                self.paintBlock(base, block, (x_coord, y_coord), block_size)

        return base



