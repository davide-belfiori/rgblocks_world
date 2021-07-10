import copy
from tkinter.constants import NO, SEL

class MissingRectInfo(Exception):
    def __init__(self):
        super().__init__()
        self.message = "No rect info available"

    def __str__(self) -> str:
        return self.message

class Block:

    def __init__(self, id, color_group, min_rect = None, rgb_value=[0,0,0]) -> None:
        self.id = id
        self.color_group = color_group
        self.min_rect = min_rect
        self.rgb_value = rgb_value

    def rgb(self):
        return self.rgb_value

    def left_edge(self):
        if self.min_rect != None:
            return self.min_rect.left_edge()
        raise MissingRectInfo
    
    def right_edge(self):
        if self.min_rect != None:
            return self.min_rect.right_edge()
        raise MissingRectInfo

    def is_vertically_aligned(self, block):
        if self.min_rect != None:
            return self.min_rect.is_vertically_aligned(block.min_rect)
        raise MissingRectInfo

    def is_over(self, block):
        if self.min_rect != None:
            return self.min_rect.is_over(block.min_rect)
        raise MissingRectInfo

    def is_under(self, block):
        if self.min_rect != None:
            return self.min_rect.is_under(block.min_rect)
        raise MissingRectInfo

    def to_left_of(self, block):
        if self.min_rect != None:
            return self.min_rect.to_left_of(block.min_rect)
        raise MissingRectInfo

    def copy(self):
        rect = self.min_rect.copy() if self.min_rect != None else None
        return Block(self.id, self.color_group, rect, copy.copy(self.rgb_value))

    def asDictionary(self):
        return {'id':self.id, 'color_group':self.color_group, 'rgb':self.rgb()}

    def __eq__(self, o: object) -> bool:
        return o != None and self.id == o.id

    def __lt__(self, o: object) -> bool:
        return self.id < o.id

    def __str__(self) -> str:
        return str(self.id)

    def __hash__(self) -> int:
        return hash(self.id)