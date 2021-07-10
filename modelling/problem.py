from modelling.stateSpaceSearch import *
from modelling.model import BlockWorldModel

class Action:
    '''
        Classe generica per la definizione di una azione di risoluzione del problema
    '''
    TYPE_GRAB = 0 # azione afferra
    TYPE_MOVE = 1 # azione sposta sopra un altro blocco
    TYPE_PUT = 2 # azione metti sul tavolo

    def __init__(self, block_id, type) -> None:
        self.block_id = block_id
        self.type = type

class Grab(Action):
    '''
        Azione 'afferra'. Descrive l'azione di afferrare un blocco da parte del robot
    '''
    def __init__(self, block_id, stack_index) -> None:
        super().__init__(block_id, Action.TYPE_GRAB)
        self.stack_index = stack_index

    def __str__(self) -> str:
        return "Grab " + str(self.block_id)

class PutOn(Action):
    '''
        Definisce l'azione di posare un blocco sopra ad un altro
    '''
    def __init__(self, block_id, dst_block_id, dst_stack_index) -> None:
        '''
            Parameti:

                block_id : object
                    Identificativo del blocco da posare
                
                dst_block_id : int
                    Identificativo del blocco sopra al quale il primo blocco verrà posato
                
                dst_stack_index : int 
                    Indice dello stack del modello al quale il blocco verrà aggiunto
        '''
        super().__init__(block_id, Action.TYPE_MOVE)
        self.dst_block_id = dst_block_id
        self.dst_stack_index = dst_stack_index

    def __str__(self) -> str:
        return "Put " + str(self.block_id) + " on " + str(self.dst_block_id)

class OnTable(Action):
    '''
        Definisce l'azione di posare un blocco sul tavolo
    '''
    def __init__(self, block_id, dst_stack_index = 0) -> None:
        '''
            Parameti:

                block_id : object
                    Identificativo del blocco da posare

                dst_stack_index : int
                    Indice dello stack vuoto del modello al quale il blocco verrà aggiunto
        '''
        super().__init__(block_id, Action.TYPE_PUT)
        self.dst_stack_index = dst_stack_index

    def __str__(self) -> str:
        return "Put " + str(self.block_id) + " on table"


class BlockWorldProblem(Problem):
    '''
        Problema Block World
        -------

        Dato un insieme di blocchi disposti su un tavolo e suddivisi in pile,
        si vuole trovare una sequenza di azioni che consenta ad un ipotetico braccio
        robotico di muovere i blocchi fino a raggiungere una certa disposizione finale.

        Regole
        -------

        - ogni blocco per essere spostato deve essere prima afferrato.
        - un solo blocco per volta può essere afferrato.
        - solo i blocchi in cima ad una pila possono essere afferrati.
        - il blocco afferrato può essere posato in cima ad una qualsiasi pila
        - il blocco afferrato può essere messo sul tavolo.

        Un generico stato del problema è rappresentato da una coppia (m, h), dove
        m rappresenta la disposizione corrente dei blocchi, mentre h è il blocco in mano al robot.
    '''

    def __init__(self, model, goal, init_hand = None, goal_hand = None):
        if isinstance(model, tuple) and isinstance(goal, tuple):
            super().__init__((model, init_hand), (goal, goal_hand))
        else:
            super().__init__((BlockWorldModel.asTuple(model), init_hand), (BlockWorldModel.asTuple(goal), goal_hand))

    def actions(self, state):

        actions = []

        # se il robot NON ha un blocco in mano...
        if state[1] == None:
            # ... può afferrare un qualsiasi blocco in cima ad uno stack
            for i,stack in enumerate(state[0]):
                if len(stack) > 0:
                    actions.append(Grab(stack[-1].id, i))
        else:
            # altrimenti ...
            for i,stack in enumerate(state[0]):
                if len(stack) > 0:
                    # ... può posare il blocco in cima ad uno stack ...
                    actions.append(PutOn(state[1].id, stack[-1].id, i))
                else:
                    # ... oppure può posarlo sul tavolo (stack vuoto)
                    actions.append(OnTable(state[1].id, i)) # posa sul tavolo in uno stack vuoto


        return actions


    def result(self, state, action):

        if action.type == Action.TYPE_GRAB:
            top_index = len(state[0][action.stack_index]) - 1
            model, hand = BlockWorldModel.modelPop(state[0], action.stack_index, top_index)
            return (model, hand)

        if action.type == Action.TYPE_MOVE:
            model = BlockWorldModel.modelAdd(state[0], state[1], action.dst_stack_index)
            return (model, None)

        if action.type == Action.TYPE_PUT:
            model = BlockWorldModel.modelAdd(state[0], state[1], action.dst_stack_index)
            return (model, None)


    def goal_test(self, state):

        # controlla se l'oggetto in mano al robot coincide con quello nello stato finale
        if state[1] != self.goal[1]:
            return False

        # controlla se tutti i blocchi nel modello corrente ed in quello finale concidono
        for i,stack in enumerate(self.goal[0]):
            if len(state[0][i]) != len(stack):
                return False
            for j,block in enumerate(stack):
                if block != state[0][i][j]:
                    return False

        return True

    def h(self, node):
        
        h = 0

        hand = node.state[1]
        target_hand = self.goal[1]
        if hand != target_hand:
            h += 1

        model = node.state[0]
        goal = self.goal[0]

        for i, stack in enumerate(model):
            for j, block in enumerate(stack):
                if self.toMove(model, i, j):
                    target_stack_idx, _ = BlockWorldProblem.block_index(goal, block.id)
                    if target_stack_idx == i:
                        h += 4
                    else :
                        h += 2
        return h

    def toMove(self, model, stack_idx, stack_pos):
        block = model[stack_idx][stack_pos]
        target = self.getBlockByIndex(stack_idx, stack_pos)

        if not (block == target):
            return True

        if stack_pos <= 0:
            return False
            
        return self.toMove(model, stack_idx, stack_pos - 1)


    def stack_match(self, stack, stack_index):
        '''
            Controlla se una pila di un modello coincide con l'equivalente nello stato goal.

            Parametri:

                stack : tuple
                    Pila del modello da confrontare

                stack_index : int
                    Indice della pila nello stato goal

            Valori restituiti:
                True se le pile coincidono, False altrimenti.
        '''

        if len(stack) != len(self.goal[0][stack_index]):
            return False

        for i,block in enumerate(stack):
            if self.goal[0][stack_index][i] != block:
                return False

        return True

    def getBlockByIndex(self, stack_idx, stack_pos, model = None):
        _model = model if model != None else self.goal[0]
        n_stack = len(_model)
        if stack_idx >= 0 and n_stack > stack_idx:
            stack = _model[stack_idx]
            stack_len = len(stack)
            if stack_pos >= 0 and stack_len > stack_pos:
                return stack[stack_pos]

        return None


    def block_index(model, block_id):
        '''
            Dato un modello ed un identificativo, restitisce gli indici del blocco associato
            a quell'identificativo.

            Parametri:

                model : tuple
                    Modello

                block_id : object
                    Identificativo del blocco

            Valore restituito:

                Coppia (i, j) dove i rappresenta l'indice della pila e j l'indice del blocco all'interno della pila.

                Se non esiste nessun blocco all'interno del modello con il dato identificativo i = j = None 
        '''
        for i,stack in enumerate(model):
            for j,block in enumerate(stack):
                if block.id == block_id:
                    return i,j
        return None, None

class ColorBasedBlockWorldProblem(Problem):
    '''
        Problema Block World basato su Colori
        -------

        Dato un insieme di blocchi disposti su un tavolo e suddivisi in pile,
        si vuole trovare una sequenza di azioni che consenta ad un ipotetico braccio
        robotico di muovere i blocchi fino a raggiungere una disposizione finale in cui 
        tutti i blocchi di uno stesso colore si trovano sulla stessa pila.

        Regole
        -------

        - ogni blocco per essere spostato deve essere prima afferrato.
        - un solo blocco per volta può essere afferrato.
        - solo i blocchi in cima ad una pila possono essere afferrati.
        - il blocco afferrato può essere posato solo in cima ad una pila
          in cui il primo blocco ha lo stesso colore di quello afferrato

        Un generico stato del problema è rappresentato da una coppia (m, h), dove
        m rappresenta la disposizione corrente dei blocchi, mentre h è il blocco in mano al robot.
    '''

    def __init__(self, model, hand = None):
        if isinstance(model, tuple):
            initial = (model, hand)
        else:
            initial = (BlockWorldModel.asTuple(model), hand)
        super().__init__(initial, None)

    def actions(self, state):

        actions = []
        # se la mano del robot è vuota ...
        if state[1] == None:
            for i,stack in enumerate(state[0]):
                # ... per ogni pila non vuota ...
                if len(stack) > 0:
                    # ... il robot può afferrare il blocco in cima alla pila
                    actions.append(Grab(stack[-1].id, i))
        else:
            # altrimenti, per ogni pila ...
            for i,stack in enumerate(state[0]):
                # se la pila non è vuota e
                # il colore del blocco in mano al robot coincide con quello in cima alla pila ...
                if len(stack) > 0 and stack[-1].color_group == state[1].color_group:
                    # ... il robot può posare il blocco in cima a questa pila
                    actions.append(PutOn(state[1].id, stack[-1].id, i))

        return actions


    def result(self, state, action):

        if action.type == Action.TYPE_GRAB:
            top_index = len(state[0][action.stack_index]) - 1
            model, hand = BlockWorldModel.modelPop(state[0], action.stack_index, top_index)
            return (model, hand)

        if action.type == Action.TYPE_MOVE:
            model = BlockWorldModel.modelAdd(state[0], state[1], action.dst_stack_index)
            return (model, None)


    def goal_test(self, state):

        if state[1] != None:
            return False

        found_colors = []

        for stack in state[0]:
            if len(stack) > 0:
                stack_col = stack[0].color_group
                try:
                    found_colors.index(stack_col)
                    return False
                except ValueError:
                    found_colors.append(stack_col)
                    if len([b for b in stack if b.color_group != stack_col]) > 0:
                        return False

        return True


    def h(self, node):

        '''
            Funzione euristica del problema Blocks World basato sui colori.
            
            Il calcolo dell'euristica tiene conto, per ogni gruppo di colore, 
            in quante pile diverse si trova almeno 1 blocco di quel gruppo.

            Se tutti i blocchi di un certo gruppo si trovano sulla stessa pila, 
            il valore associato a tale gruppo è 0, altrimenti si aggiunge 1 per ogni ulteriore pila.

            Infie si sommano tutti i valori calcolati per ogni gruppo di colore 
            e si aggiunge 1 se in quello stato il robot ha un blocco in mano.
        '''
        
        h = 0 if node.state[1] == None else 1

        color_group_values = {}

        for stack in node.state[0]:
            colors_in_stack = unique(map(lambda b : b.color_group, stack))
            for color_group in colors_in_stack:
                    if color_group in color_group_values:
                        color_group_values[color_group] += 1
                    else:
                        color_group_values[color_group] = 0
            
            # found_colors = []
            # for block in stack:
            #     if not block.color_group in found_colors:
            #         found_colors.append(block.color_group)
            #         if block.color_group in color_group_values:
            #             color_group_values[block.color_group] += 1
            #         else:
            #             color_group_values[block.color_group] = 0

        h += sum(color_group_values.values())
        return h
