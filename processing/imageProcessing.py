import numpy as np
from cv2 import cv2 as cv
from processing.geometry import mean_point

SOBEL_GRADIENT_X = 1
SOBEL_GRADIENT_Y = 2

class Blob:

    def __init__(self, contour, contour_approximation = 3) -> None:
        self.contour = contour
        self.contourArea = cv.contourArea(contour)
        self.boundingRect = self.calc_bounding_rect(contour)
        self.minRect = self.calc_min_rect(contour, contour_approximation)
        self.center = mean_point(self.minRect[0], self.minRect[2])

    def calc_min_rect(self, contour, contour_approximation = 3):
        contour_poly = cv.approxPolyDP(contour, contour_approximation, True)
        minRect = cv.minAreaRect(contour_poly)
        return cv.boxPoints(minRect)

    def calc_bounding_rect(self, contour):
        boundingRect = cv.boundingRect(contour)
        p0 = np.array([boundingRect[0], boundingRect[1]])
        p1 = np.array([boundingRect[0] + boundingRect[2], boundingRect[1]])
        p2 = np.array([boundingRect[0] + boundingRect[2], boundingRect[1] + boundingRect[3]])
        p3 = np.array([boundingRect[0], boundingRect[1] + boundingRect[3]])

        return np.array([p0,p1,p2,p3])

def saveImage(img, filename="image.jpg"):
    cv.imwrite(filename, img)

def BGRtoRGB(frame):
    return cv.cvtColor(frame, code=cv.COLOR_BGR2RGB)

def GRAYtoRBG(frame):
    return cv.cvtColor(frame, code=cv.COLOR_GRAY2RGB)

def blank(height = 100, width = 100, depth = 0, pixel_tipe=np.uint8):
    if width > 0 and height > 0 :
        if depth > 0:
            return np.zeros(shape=(height, width, depth), dtype=pixel_tipe)
        return np.zeros(shape=(height, width), dtype=pixel_tipe)
    return []

def hstack(img1, img2):
    return cv.hconcat(src=[img1, img2])

def vstack(img1, img2):
    return cv.vconcat(src=[img1, img2])

def crop(frame, p1, p2):
    if p1.x  < p2.x :
        if p1.y < p2.y :
            return frame[p1.y : p2.y, p1.x : p2.x]           
        return frame[p2.y : p1.y, p1.x : p2.x]
    if p1.y < p2.y:
        return frame[p1.y : p2.y, p2.x : p1.x]

    return frame[p2.y : p1.y, p2.x : p1.x]

def subtract(img1, img2):
    return cv.subtract(img1, img2)

def bitAnd(img1, img2):
    return cv.bitwise_and(img1, img2)

def bitOr(img1, img2):
    return cv.bitwise_or(img1, img2)

def sub_frame(frame, contour):
    '''
    Given a frame and a contuor, sets all the pixels of the frame that are NOT INSIDE the contour to 0.
    '''
    mask =  np.zeros(shape=frame.shape, dtype=np.uint8)
    cv.drawContours(mask, [np.int0(contour)], 0, color=(255,255,255),  thickness=cv.FILLED)
    return bitAnd(frame, mask)

def correct_brightness(frame, alpha, beta):
    return cv.convertScaleAbs(frame, alpha=alpha, beta=beta)


def sobel(frame, kernel_size = 3, scale = 1, delta = 0, gradient_dir = 0):
    if len(frame.shape) == 3:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    else: gray = frame
    grad_x = cv.Sobel(gray, cv.CV_16S, 1, 0, ksize=kernel_size, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    grad_y = cv.Sobel(gray, cv.CV_16S, 0, 1, ksize=kernel_size, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    abs_grad_x = cv.convertScaleAbs(grad_x)
    abs_grad_y = cv.convertScaleAbs(grad_y)

    if gradient_dir == 1:
        return abs_grad_x
    if gradient_dir == 2:
        return abs_grad_y

    grad = cv.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    return grad


def binary_threshold(frame, threshold):
    ret,filtered = cv.threshold(frame, threshold, 255, cv.THRESH_BINARY)
    return filtered


def extractColorHSV(image, lowerHSV, upperHSV):
    '''
    Estrae da una immagine tutti i pixel che rientrano in un dato intervallo di colore
    '''
    # Converte il frame da RGB ad HSV
    image_hsv = cv.cvtColor(image, cv.COLOR_RGB2HSV)
    # Estrae i pixel che rientrano nel range
    mask = cv.inRange(image_hsv, lowerHSV, upperHSV)
    return mask

def blur(frame, kernel_size = 3):
    if kernel_size >= 3:
        if kernel_size % 2 == 0:
            kernel_size = kernel_size - 1
        return cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    return frame

def erosion(frame, size = 3, shape = cv.MORPH_RECT):
    element = cv.getStructuringElement(shape, (size, size), (size // 2, size // 2))
    return cv.erode(frame, element)

def dilation(frame, size = 3, shape = cv.MORPH_RECT):
    element = cv.getStructuringElement(shape, (size, size), (size // 2, size // 2))
    return cv.dilate(frame, element)

def close(frame, size=3, shape = cv.MORPH_RECT):
    element = cv.getStructuringElement(shape, (size, size), (size // 2, size // 2))
    return cv.morphologyEx(frame, cv.MORPH_CLOSE, element)


def find_contours(frame):
    contours, _ = cv.findContours(frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return contours


def find_blobs(frame, min_contour_area = 0, contour_approx = 3):

    contours = find_contours(frame)
    blob_list = list()
    for c in contours :
        c_area = cv.contourArea(c)
        if c_area >= min_contour_area:
            blob_list.append(Blob(c, contour_approx))

    return blob_list