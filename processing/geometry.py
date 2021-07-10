import math

import copy

class InvalidCoordinateIndex(Exception):
    def __init__(self, index) -> None:
        super.__init__()
        self.message = "Invalid coordinate index" + str(index)

class Point:
    def __init__(self, x = 0, y = 0) :
        self.x = x
        self.y = y

    def as_tuple(self):
        '''
        Return x and y coordinates of this point as a tuple
        '''
        return (self.x, self.y)

    def as_int_tuple(self):
        '''
        Return x and y coordinates of this point as an integer tuple
        '''
        return (int(self.x), int(self.y))

    def __getitem__ (self, key):
        if isinstance(key, int):
            if key == 0: return self.x
            if key == 1: return self.y
        raise InvalidCoordinateIndex(key)

    def  __eq__(self, other):
        '''
        Two points are equals if they have the same coordinates
        '''
        return self.x == other.x and self.y == other.y

def point_distance(p1, p2) :
    '''
    Return the Euclidean distance of the given points
    '''
    if isinstance(p1, Point) and isinstance(p2, Point):
        a = abs(p2.x - p1.x)
        b = abs(p2.y - p1.y)
    else:
        a = abs(p2[0] - p1[0])
        b = abs(p2[1] - p1[1])

    return math.sqrt(a**2 + b**2)

def mean_point(p1, p2):
    '''
    Return the Mean Point of the given points
    '''
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return Point(p1[0] + dx / 2, p1[1] + dy / 2)

def point_translate(point, vec):
    '''
    Translate the given point by a 2D vector
    '''
    return Point(point.x + vec[0], point.y + vec[1])

def segment_mean_point(segment):
    '''
    Return the Mean Point of a segment.

    ``segment`` = point tuple that represent a segment
    '''
    return mean_point(segment[0], segment[1])

def segment_length(segment):
    '''
    Return the length of a segment.

    ``segment`` : point tuple that represent a segment
    '''
    return point_distance(segment[0], segment[1])

class Rect:

    def __init__(self, rect):
        self.rect = rect
        self.center = mean_point(self.rect[0], self.rect[2])

    def copy(self):
        return Rect(copy.copy(self.rect))

    def top_edge(self):
        top_edge_points = [Point(p[0], p[1]) for p in self.rect if p[1] <= self.center.y]
        if len(top_edge_points) == 2 :
            return top_edge_points
        top_edge_points.sort(key = lambda p : p.y)
        return [top_edge_points[0], top_edge_points[1]]

    def bottom_edge(self):
        bottom_edge_points = [Point(p[0], p[1]) for p in self.rect if p[1] >= self.center.y]
        if len(bottom_edge_points) == 2 :
            return bottom_edge_points
        bottom_edge_points.sort(key = lambda p : p.y, reverse=True)
        return [bottom_edge_points[0], bottom_edge_points[1]]

    def left_edge(self):
        left_edge_points = [Point(p[0], p[1]) for p in self.rect if p[0] <= self.center.x]
        if len(left_edge_points) == 2 :
            return left_edge_points
        left_edge_points.sort(key = lambda p : p.x)
        return [left_edge_points[0], left_edge_points[1]]

    def right_edge(self):
        right_edge_points = [Point(p[0], p[1]) for p in self.rect if p[0] >= self.center.x]
        if len(right_edge_points) == 2 :
            return right_edge_points
        right_edge_points.sort(key = lambda p : p.x, reverse=True)
        return [right_edge_points[0], right_edge_points[1]]

    def width(self):
        return segment_length(self.top_edge())
        # return max(segment_length(self.top_edge()), 
        #            segment_length(self.bottom_edge()))

    def height(self):
        return segment_length(self.left_edge())
        # return max(segment_length(self.left_edge()), 
        #             segment_length(self.right_edge()))


    def is_vertically_aligned(self, other):
        half_width = self.width() / 2
        return other.center.x >= self.center.x - half_width and \
               other.center.x <= self.center.x + half_width

    def is_horizontaly_aligned(self, other):
        half_height = self.height() / 2
        return other.center.y >= self.center.y - half_height and \
               other.center.y <= self.center.y + half_height

    def is_over(self, other):
        return self.center.y < other.center.y

    def is_under(self, other):
        return not self.is_over(other)

    def to_right_of(self, other):
        return self.center.x > other.center.x

    def to_left_of(self, other):
        return not self.to_right_of(other)

    def translate(self, vec):
        self.center.x = self.center.x + vec[0]
        self.center.y = self.center.y + vec[1]

        for p in self.rect:
            p[0] = p[0] + vec[0]
            p[1] = p[1] + vec[1]
