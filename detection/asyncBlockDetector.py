from detection.imageSource import *
from utils.channel import Channel
from detection.blockDetection import find_blocks
from processing import imageProcessing as ip
from processing import imageEditor as editor
from processing.geometry import point_translate
from modelling.model import ModelBuilder
import threading

class AsyncBlockDetector:
    def __init__(self, settings, colors) -> None:
        self.imageSource = None
        self.captureTaskRunning = False
        self.settings = settings
        self.colors = colors

    def setImageSource(self, imageSource):
        if not self.captureTaskRunning:
            self.imageSource = imageSource

    def use(self, settings = None, colors = None):
        if settings != None:
            self.settings = settings
        if colors != None:
            self.colors = colors

    def start(self, initCallback = lambda:()):
        if not self.captureTaskRunning:
            asyncChannel = Channel()
            self.asyncClient = asyncChannel.registerClient()
            cap_t = threading.Thread(target=self.capture, args=[asyncChannel.server, self.imageSource, initCallback, self.handleError])
            cap_t.start()
            self.captureTaskRunning = True

    def get(self, block = True):
        if self.captureTaskRunning:
            return self.asyncClient.receive(block)

    def stop(self, releaseImageSource = True):
        if self.captureTaskRunning :
            self.asyncClient.send({"detect":False, "release_source":releaseImageSource})
            self.captureTaskRunning = False

    def handleError(self):
        self.captureTaskRunning = False

    def capture(self, endpoint, imageSource, onInit, onError):
        if not imageSource.ready:
                try:
                    imageSource.initialize()
                except:
                    endpoint.send({"error": "Errore di inizializzazione della sorgente immagine"})
                    onError()
                    return
        onInit()
        message = None
        detect = True

        while detect:

            message = endpoint.receive()
            if message != None:
                detect = message["detect"] if "detect" in message else detect
            
            if detect and endpoint.outputSize() < 10:
                # try to get the next frame
                try:
                    frame = imageSource.next_image()
                except:
                    endpoint.send({"error": "Errore sorgente immagine. Impossibile continure la ricerca."})
                    onError()
                    return

                settings = self.settings
                colors = self.colors
                
                # apply bright and blur filters
                frame = ip.correct_brightness(frame, settings["bright_gain"], settings["bright_offset"])
                if settings["blur_size"] >= 3:
                    frame = ip.blur(frame, kernel_size=settings["blur_size"])

                # Detect blocks in frame
                # - blocks = list of blocks found
                # - mask = extracted color mask
                # - contours = extracted color contours
                # - sub = mask - contours
                blocks, mask, contours, sub = find_blocks(frame, settings, colors)

                mask = ip.GRAYtoRBG(mask)
                contours = ip.GRAYtoRBG(contours)
                sub = ip.GRAYtoRBG(sub)


                # Draw blocks over frame
                for block in blocks:
                    editor.draw_point(frame, block.min_rect.center)
                    editor.draw_box(frame, block.min_rect.rect)
                    editor.write_text(frame, str(block), point_translate(block.min_rect.center, (-40, -10)), color=editor.WHITE, font_scale=0.6, thickness=1)

                    editor.draw_point(mask, block.min_rect.center)
                    editor.draw_box(mask, block.min_rect.rect)
                    editor.write_text(mask, str(block), point_translate(block.min_rect.center, (-40, -10)), color=editor.RED, font_scale=0.6, thickness=1)

                    editor.draw_point(contours, block.min_rect.center)
                    editor.draw_box(contours, block.min_rect.rect)
                    editor.write_text(contours, str(block), point_translate(block.min_rect.center, (-40, -10)), color=editor.RED, font_scale=0.6, thickness=1)

                    editor.draw_point(sub, block.min_rect.center)
                    editor.draw_box(sub, block.min_rect.rect)
                    editor.write_text(sub, str(block), point_translate(block.min_rect.center, (-40, -10)), color=editor.RED, font_scale=0.6, thickness=1)
                
                
                model = ModelBuilder.build(block_list=blocks)

                obj = {
                    "frame": frame,
                    "model": model,
                    "mask": mask,
                    "contours": contours,
                    "sub": sub
                }
                endpoint.send(obj)


        if message["release_source"]:
            imageSource.release()
            