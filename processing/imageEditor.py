from processing.geometry import Point
from cv2 import cv2 as cv
import numpy as np

RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)

def draw_point(frame, point, color = RED, size = 4):
    if isinstance(point, Point) :
        cv.circle(frame, point.as_int_tuple(), size, color, -1)
    else: cv.circle(frame, point, size, color, -1)


def draw_box(frame, box, color = RED, thickness = 2):
    cv.drawContours(frame, [np.int0(box)], 0, color, thickness)


def draw_square(frame, size, org, color):
    cv.rectangle(frame, org, (org[0] + size, org[1] + size), color=color, thickness= -1)


def write_text(frame, text, point, color = WHITE, font_scale = 1, thickness = 2):
    if isinstance(point, Point) :
        cv.putText(frame, text, point.as_int_tuple(), cv.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    else: cv.putText(frame, text, point, cv.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)


def blank(frame_width, frame_height):
    return np.zeros(shape=(frame_height, frame_width), dtype=np.uint8)
