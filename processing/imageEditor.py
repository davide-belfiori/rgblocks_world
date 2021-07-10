from processing.geometry import Point
from cv2 import cv2 as cv
import numpy as np
# import functools 

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

# def draw_model(model, frame_width = 600, frame_height = 600, highlight_blocks_id = []):
#     img = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
#     block_size = clac_block_size(model, frame_width, frame_height)

#     for i,stack in enumerate(model):
#         x_coord = block_size * i
#         stack_len = len(stack)
#         for j,block in enumerate(stack):
#             y_coord = frame_height - block_size * (stack_len - j)
#             draw_square(img, block_size, (x_coord, y_coord), color=block.rgb_value)
#             draw_point(img, (x_coord + block_size // 2, y_coord + block_size // 2), color=WHITE)
#             write_text(img, block.id, (x_coord + 5, y_coord + 20), color=(30,30,30), font_scale=0.5)
#             if block.id in highlight_blocks_id:
#                 cv.circle(img, (x_coord + block_size // 2, y_coord + block_size // 2), 20, WHITE, 4)


#     return img


# def clac_block_size(model, frame_width, frame_height):
#     n_stack = len(model)
#     if n_stack == 0:
#         return 0
#     max_stack_len = len(functools.reduce(lambda s1, s2 : s1 if len(s1) > len(s2) else s2, model))
#     if max_stack_len == 0:
#         return 0
#     max_block_width = frame_width // n_stack
#     max_block_height = frame_height // max_stack_len

#     return min(max_block_width, max_block_height)
