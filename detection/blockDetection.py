import numpy as np
from math import ceil, floor

from modelling.block import Block
import processing.imageProcessing as ip
import processing.geometry as geo


def find_blocks(frame, settings, colors):

    blocks = list()
    mask = np.array([])
    contours = np.array([])
    sub = np.array([])

    for color in colors:
        found, color_mask, color_contours, sub_mask = find_blocks_by_color(frame, 
                                                                    color, settings["subtract_contours"],
                                                                    settings["min_contour_area"], settings["ca_scale_factor"], 
                                                                    settings["max_edge_ratio"], settings["min_contour_completeness"],
                                                                    settings["contour_dilation"], settings["contour_threshold"], settings["cd_scale_factor"], 
                                                                    settings["close_size"],
                                                                    1, settings["max_search_steps"])
        for i, block in enumerate(found):
            block.id += ("_" + str(i))

        blocks.extend(found)

        if len(mask) == 0:
            mask = color_mask
        else:
            mask = ip.bitOr(mask, color_mask)
        
        if len(contours) == 0:
            contours = color_contours
        else:
            contours = ip.bitOr(contours, color_contours)

        if len(sub) == 0:
            sub = sub_mask
        else:
            sub = ip.bitOr(sub, sub_mask)

    return blocks, mask, contours, sub


def find_blocks_by_color(frame, color, subtract_contours=True,
                        min_contour_area = 2000, ca_scale_factor = 0.9, 
                        max_edge_ratio = 1.4, min_contour_completeness = 75,
                        contour_dilation = 7, contour_threshold = 20, cd_scale_factor = 1.5,  
                        close_size = 3,
                        search_step = 1, max_search_steps = 3):

    # estrai la maschera di colore
    maschera_colore = ip.extractColorHSV(frame, color.lowerHSV(), color.upperHSV())

    # estari i contorni
    maschera_contorni = ip.sobel(frame)
    # scarta i contorni più deboli
    maschera_contorni = ip.binary_threshold(maschera_contorni, contour_threshold)
    # dilata i contorni
    if contour_dilation >= 3:
        maschera_contorni = ip.dilation(maschera_contorni, size=contour_dilation)

    # sottrai i contorni dalla maschera di colore
    maschera_differenza = ip.subtract(maschera_colore, maschera_contorni)
    # applica un filtro a chiusura
    if close_size >= 3:
        maschera_differenza = ip.close(maschera_differenza, close_size)

    # cerca le regioni colorate
    if subtract_contours:
        blob_list = ip.find_blobs(maschera_differenza, min_contour_area)
    else:
        blob_list = ip.find_blobs(maschera_colore, min_contour_area)

    blocks = list()

    # processa le regioni per trovare i blocchi effettivi
    for blob in blob_list:

        # ontrolla se una regione è valida
        if contour_completeness(blob) >= min_contour_completeness and edge_ratio(blob.minRect) < max_edge_ratio :
            toAppend = Block(id = color.color_id,
                                color_group = color.color_group,
                                min_rect = geo.Rect(blob.minRect),
                                rgb_value=color.RGB())
            blocks.append(toAppend)

        elif search_step <= max_search_steps:
            # get from original frame only pixels included in blob contours
            sub_frame = ip.sub_frame(frame, blob.contour)

            # try to find boxex in the sub-frame modifing search parameters
            found,_,_,_ = find_blocks_by_color(sub_frame, color, subtract_contours=True,
                                         min_contour_area = min_contour_area * ca_scale_factor, ca_scale_factor = ca_scale_factor,
                                         max_edge_ratio=max_edge_ratio, min_contour_completeness=min_contour_completeness,
                                         contour_dilation = int(contour_dilation * cd_scale_factor), contour_threshold = contour_threshold, cd_scale_factor = cd_scale_factor,
                                         close_size = close_size,
                                         search_step = search_step + 1)
            for box in found:
                blocks.append(box)


    return blocks, maschera_colore, maschera_contorni, maschera_differenza


def edge_ratio(box):

    e1 = geo.point_distance(box[0], box[1])
    e2 = geo.point_distance(box[1], box[2])

    return max(e1, e2) / (1.e-5 + min(e1, e2))


def void_area(blob):

    e1 = geo.point_distance(blob.minRect[0], blob.minRect[1])
    e2 = geo.point_distance(blob.minRect[1], blob.minRect[2])

    rect_area = e1 * e2
    diff = rect_area - blob.contourArea
    return diff * 100 / (1.e-5 + rect_area)


def contour_completeness(blob):

    e1 = geo.point_distance(blob.minRect[0], blob.minRect[1])
    e2 = geo.point_distance(blob.minRect[1], blob.minRect[2])
    rect_area = e1 * e2

    return blob.contourArea * 100 / (1.e-5 + rect_area)


def round_edge_ratio(er):
    dec = er - floor(er)
    if dec <= 0.4 :
        return floor(er)

    return ceil(er)
