from cv2 import cv2 as cv
import time

class CaptureExcetpion(Exception):    
    def __init__(self, message="Camera capture error. Can't receive frame") -> None:
        super().__init__()
        self.message = message

class ImageFormatException(Exception):
    def __init__(self, message="Image format not supported") -> None:
        super().__init__()
        self.message = message

class ImageReadingException(Exception):
    def __init__(self, message="Error loading image") -> None:
        super().__init__()
        self.message = message


class ImageSource:
    def __init__(self, initialize = True) -> None:
        self.ready = False
        if initialize:
            self.initialize()

    def initialize(self):
        self.ready = True

    def next_image(self):
        pass

    def release(self):
        self.ready = False


class Camera(ImageSource):

    def __init__(self, frame_width = 640, frame_height = 480, color_format = cv.COLOR_BGR2RGB, init_camera = True):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.color_format = color_format
        super().__init__(initialize = init_camera)

    def set_capture_shape(self, shape):
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, shape[0])
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, shape[1])

    def set_color_format(self, color_format):
        self.color_format = color_format

    def initialize(self):
        time.sleep(10.0)
        self.capture = cv.VideoCapture(0)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.ready = True

    def next_image(self):
        ret, frame = self.capture.read()
        if not ret:
            raise CaptureExcetpion
        if self.color_format != None:
            frame = cv.cvtColor(frame, self.color_format)

        return frame

    def release(self):
        super().release()
        self.capture.release()


class ImageFile(ImageSource):

    def __init__(self, filename, color_format = cv.COLOR_BGR2RGB, initialize = True) -> None:
        self.filename = filename
        self.color_format = color_format
        super().__init__(initialize=initialize)

    def set_color_format(self, color_format):
        self.color_format = color_format

    def initialize(self):
        try:    
            self.image = cv.imread(self.filename)
        except:
            raise ImageReadingException
        
        if len(self.image.shape) != 3:
            raise ImageFormatException

        self.ready = True

    def next_image(self):
        if self.color_format:
            return cv.cvtColor(self.image, self.color_format)
        return self.image

    def release(self):
        super().release()
        self.image = None
    
