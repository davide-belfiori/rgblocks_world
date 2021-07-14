import numpy as np

from modelling.block import Block
import processing.imageProcessing as ip
import processing.geometry as geo


def find_blocks(frame, settings, colors):

    blocks = list() # lista di blocchi riconosciuti
    mask = np.array([]) # maschera di colore
    contours = np.array([]) # maschera dei bordi
    sub = np.array([]) # maschera differenza

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

    '''
        Restituisce la lista dei blocchi di un dato colore riconosciuti all'interno di una immagine.

        Parametri:
        - frame: immagine (intesa in formato RGB)
        - color: colore
        - subtract_contours: flag booleano che indica se utilizzare o meno la sottrazione dei bordi per il riconoscimento dei blocchi
        - min_contour_area: area minima di accettazione di una regione di colore
        - ca_scale_factor: fattore di scala dell'area minima di accettazione del contorno
        - max_edge_ratio: rapporto massimo tra le dimensioni del rettangolo minimo di una regione di colore
        - min_contour_completeness: percentuale minima di completezza dell'area di una regione di colore rispetto al suo rettangolo minimo
        - contour_dilation: fattore di dilatazione della maschera dei contorni
        - contour_threshold: soglia di luminosità della maschera dei contorni
        - cd_scale_factor: fattore di scala del valore di dilatazione
        - close_size: fattore di chiusura della maschera differenza
        - search_step: indice di iterazione
        - max_search_steps: numero massimo di iterazioni

        Restituisce:
        - lista di blocchi riconosciuti
        - maschera di colore
        - maschera dei bordi
        - differenza tra maschera di colore e maschera dei bordi
    '''

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

        # controlla se una regione è valida
        if contour_completeness(blob) >= min_contour_completeness and edge_ratio(blob.minRect) < max_edge_ratio :
            toAppend = Block(id = color.color_id,
                                color_group = color.color_group,
                                min_rect = geo.Rect(blob.minRect),
                                rgb_value=color.RGB())
            blocks.append(toAppend)

        elif search_step <= max_search_steps:
            # estrai dall'immagine originale solo i pixel compresi nel contorno della regione
            sub_frame = ip.sub_frame(frame, blob.contour)

            # affina la ricerca modificando i parametri di riconoscimento
            found,_,_,_ = find_blocks_by_color(sub_frame, color, subtract_contours=True,
                                         min_contour_area = min_contour_area * ca_scale_factor, ca_scale_factor = ca_scale_factor,
                                         max_edge_ratio=max_edge_ratio, min_contour_completeness=min_contour_completeness,
                                         contour_dilation = int(contour_dilation * cd_scale_factor), contour_threshold = contour_threshold, cd_scale_factor = cd_scale_factor,
                                         close_size = close_size,
                                         search_step = search_step + 1)
            for block in found:
                blocks.append(block)


    return blocks, maschera_colore, maschera_contorni, maschera_differenza


def edge_ratio(box):
    '''
        Calcola il rapporto tra i lati di un rettangolo.
    '''
    e1 = geo.point_distance(box[0], box[1])
    e2 = geo.point_distance(box[1], box[2])

    return max(e1, e2) / (1.e-5 + min(e1, e2))


def contour_completeness(blob):
    '''
        Calcola la percentuale di completezza dell'area di una regione
        rispetto all'area del suo rettangolo minimo.
    '''
    e1 = geo.point_distance(blob.minRect[0], blob.minRect[1])
    e2 = geo.point_distance(blob.minRect[1], blob.minRect[2])
    rect_area = e1 * e2

    return blob.contourArea * 100 / (1.e-5 + rect_area)
