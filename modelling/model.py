from modelling.utils import mode
import processing.geometry as geo
import functools
import json
from modelling.block import Block
import itertools
import random

class ModelLoadingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return "Errore durante il caricamento del modello."

class ModelBuilder():

    def build(block_list : list):

        # inizializza il modello come una lista vuota
        model = []

        # se la lista dei blocchi non è vuota
        if len(block_list) > 0:
            
            # calcola la massima larghezza di un blocco 
            max_block_width = functools.reduce(lambda b1, b2: b1 if b1.min_rect.width() > b2.min_rect.width() else b2, block_list).min_rect.width()
            
            # ordina i blocchi in ordine crescente secondo la coordinata x del centro del rettangolo minimo
            block_list.sort(key=lambda b : b.min_rect.center.x)

            # finchè la lista non è vuota ...
            while len(block_list) > 0:
                # ... rimuovi il primo blocco ...
                block = block_list.pop(0)
                # ... ed aggiungilo al modello
                ModelBuilder.add_block(model, block)

            # completa il modello aggiungendo le pile vuote
            ModelBuilder.add_empty_stacks(model, max_block_width)

        return model


    def add_empty_stacks(model, min_distance):
        '''
            Aggiunge al modello le pile vuote.

            Due pile vuote vengono sempre aggiunte, una all'inizio ed una alla fine del modello.
            Un pila vuota viene aggiunta tra due pile adiacenti se la distanza tra loro e maggiore
            di ``min_distance``.
        '''
        # parti dalla prima pila
        stack_idx = 0
        while stack_idx < len(model) - 1:
            # considera i primi blocchi delle due pile adiacenti
            b1 = model[stack_idx][-1] 
            b2 = model[stack_idx + 1][-1]
            # calcola la distanza in pixel tra i blocchi adiacenti
            block_distance = geo.segment_mean_point(b2.left_edge()).x \
                             - geo.segment_mean_point(b1.right_edge()).x

            if block_distance > min_distance:
                # se questa distanza e' maggoire della larghezza massima dei blocchi
                # aggiungi tante pile vuote quante il risultato della divisione intera tra
                # la distanza e la larghezza massima 
                for _ in range(int(block_distance // min_distance)):
                    model.insert(stack_idx + 1, list([]))
                    stack_idx += 1

            stack_idx += 1
            
        # aggiungi le pile vuote 
        # all'inizio ed alla fine del modello
        model.insert(0, list([]))
        model.append(list([]))


    def add_new_stack(model, index, block):
        '''
        Add one new single block stack to a model in the specified index
        '''
        # insert a new single block stack
        model.insert(index, list([block]))


    def add_to_stack(model, block, stack_index):
        ''' 
            Aggiunge un blocco ad una pila esistente di un modello.
            
            NOTA: Il blocco in posizione 0 di una pila è quello che si trova più in basso.
        '''
        # considerio il blocco più in basso nella pila
        stack_pos = 0
        # finchè tutti i blocchi nella pila non sono stati confrontati ...
        while stack_pos < len(model[stack_index]):
            # ... se il blocco da aggiungere si trova SOTTO al blocco corrente nella pila ...
            if block.is_under(model[stack_index][stack_pos]):
                # ... aggiungo il nuovo blocco nella posizione corrente
                model[stack_index].insert(stack_pos, block)
                return
            # altrimenti passo al blocco successivo
            stack_pos += 1
        # se il nuovo blocco si trova sopra a tutti gli altri,
        # lo aggiungo in cima alla pila
        model[stack_index].append(block)


    def add_block(model, block, index = 0):
        '''
            Aggiunge un nuovo blocco ad un modello
        '''
        # se il modello è vuoto
        # oppure tutte le pile sono state esaminate ...
        if len(model) == 0 or index >= len(model):
            # ... aggiungi il blocco ad una nuova pila
            ModelBuilder.add_new_stack(model, index, block)
            return

        # se la pila non è vuota ...
        if len(model[index]) > 0:
            # considera il blocco in cima alla pila
            b = model[index][-1]
            # se il blocco da aggiungere si trova 
            # sopra o sotto a questo blocco ...
            if block.is_vertically_aligned(b):
                # ... aggiungi il nuovo blocco a questa pila
                ModelBuilder.add_to_stack(model, block, index)
                return

        # confronta il blocco con la prossima pila  
        ModelBuilder.add_block(model, block, index = index + 1)


class BlockWorldModel():

    def loadFromFile(filename):
        '''
            Carica un modello da file
        '''
        try:
            with open(filename) as modelFile:
                j_model = json.load(modelFile)
                model = list()
                for stack in j_model:
                    new_stack = list()
                    for block in stack:
                        b = Block(block["id"], block["color_group"], None, block["rgb"])
                        new_stack.append(b)
                    model.append(new_stack)
                return model
        except:
            raise ModelLoadingException()

    def saveModel(model, filename):
        '''
            Salva il modello come file
        '''
        dict = BlockWorldModel.asDictionary(model)
        with open(filename, "w") as outfile:
            json.dump(dict, outfile)

    def asDictionary(model):
        '''
            Restituisce una copia del modello sotto forma di dizionario
        '''
        dict = list()
        for stack in model:
            dict_stack = list()
            for block in stack:
                b_dict = block.asDictionary()
                dict_stack.append(b_dict)
            dict.append(dict_stack)

        return dict
    
    def asList(model):
        '''
            Restituisce una copia del modello sotto forma di lista
        '''
        new_model = list()
        for stack in model:
            new_stack = list()
            for block in stack:
                b_copy = block.copy()
                new_stack.append(b_copy)
            new_model.append(new_stack)
        return new_model


    def asTuple(model):
        '''
            Restituisce una copia del modello sotto forma di tupla
        '''
        new_model = list()
        for stack in model:
            new_stack = list()
            for block in stack:
                b_copy = block.copy()
                new_stack.append(b_copy)
            new_model.append(tuple(new_stack))
        return tuple(new_model)


    def shuffle(model, seed = None):
        '''
            Restituisce una disposizione casuale dei blocchi del modello,
            mantenendo invariato il nomero di pile
        '''
        random.seed(seed)
        rand_model = [] 
        for _ in range(0, len(model)):
            rand_model.append([])

        blocks = list(itertools.chain.from_iterable(model))
        while len(blocks) > 0:
            block_idx = random.randint(0, len(blocks) - 1)
            block = blocks.pop(block_idx)
            stack_idx = random.randint(0, len(model) - 1)
            rand_model[stack_idx].append(block.copy())

        return rand_model

    def random_block_list(n_blocks, colors, seed = None):
        """
            Genera una lista casuale di blocchi
        """
        if seed != None:
            random.seed(seed)

        block_list = []
        # assegno un contatore per ogni colore
        color_counter = list(map(lambda color: [color, 0], colors))
        for _ in range(n_blocks):
            # estraggo casualmente l'indice di un colore tra quelli disponibili
            color_idx = random.randint(0, len(colors) - 1)
            # seleziono il colore
            color = colors[color_idx]
            # utilizzo il contatore del colore per generare l'id del blocco
            color_id = color.color_id + "_" + str(color_counter[color_idx][1])
            # aggiungo un nuovo blocco alla lista
            block_list.append(Block(id = color_id,
                                    color_group = color.color_group,
                                    rgb_value = color.RGB()))
            # incremento il contatore del blocco
            color_counter[color_idx][1] += 1

        return block_list

    def random(n_blocks, colors, seed = None):
        """
            Genera un modello casuale.
        """
        if seed != None:
            random.seed(seed)
        # genero una lista casuale di blocchi
        bList = BlockWorldModel.random_block_list(n_blocks = n_blocks, colors = colors)
        # inizializzo un modello vuoto
        model = []
        while len(bList) > 0:
            # estraggo un blocco a caso dalla lista
            block_idx = random.randint(0, len(bList) - 1)
            block = bList.pop(block_idx)
            if random.randint(0,1) > 0 and len(model) > 0:
                # aggiungo il blocco estratto ad una pila casuale
                stack_idx = random.randint(0, len(model) - 1)
                model[stack_idx].append(block)
            else:
                # aggiungo il blocco estratto ad una nuova pila
                model.append([block])

        model.insert(0, list([]))
        model.append(list([]))
        return model

    def modelPop(model, stack_index, block_index):
        '''
            Rimuove un blocco da un modello.

            Parametri:
                model : tuple
                    Modello

                stack_index : int
                    Indice dello stack dal quale rimuovere il blocco
                
                block_index : int
                    Indice del blocco da rimuovere all'interno dello stack

            Valori restituiti:

                La funzione restituisce una coppia formata dal nuovo modello e dal blocco rimosso.
        '''
        new_model = list()
        toReturn = None

        for i,stack in enumerate(model):

            new_stack = list()
            for j,block in enumerate(stack):
                b_copy = block.copy()
                if i != stack_index or j != block_index:
                    new_stack.append(b_copy)
                else :
                    toReturn = b_copy

            new_model.append(tuple(new_stack))

        return tuple(new_model), toReturn


    def modelAdd(model, block, stack_index):
        '''
            Aggiunge un blocco al modello. 
            Il nuovo blocco viene aggiunto in cima allo stack corrispondente
            al dato indice.

            Parametri:
                model : tuple
                    Modello
                
                block : Block 
                    Blocco da aggiungere
                
                stack_index : int
                    Indice dello stack al quale il blocco deve essere aggiunto

            Valori restituiti:
            
                La funzione restituisce una tupla che rappresenta il nuovo modello con il blocco aggiunto.
        '''
        new_model = list()

        for i,stack in enumerate(model):
            new_stack = list()
            # prima copia l'intera pila
            for b in stack:
                b_copy = b.copy()
                new_stack.append(b_copy)
            # se la pila corrente corrisponde a quella data ...
            if i == stack_index:
                # ... aggiunge il nuovo blocco in cima alla pila
                new_stack.append(block.copy())

            new_model.append(tuple(new_stack))

        return tuple(new_model)


    # # restituisce un NUOVO STATO con un nuovo stack composto dal blocco specificato
    # def modelAppend(model, block, stack_index):
    #     '''
    #         Aggiunge un 
    #     '''
    #     new_model = list()

    #     for stack in model:
    #         new_stack = list()
    #         for b in stack:
    #             b_copy = b.copy()
    #             new_stack.append(b_copy)
    #         new_model.append(tuple(new_stack))

    #     if stack_index == len(new_model):
    #         new_model.append((block,))
    #     elif stack_index == 0:
    #         new_model.insert(0, (block,))
    #     else:
    #         new_model[stack_index] = (block,)

    #     return tuple(new_model)

    
