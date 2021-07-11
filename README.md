# **RGBlocks World**

**RGBlocks World** è una applicazione dimostrativa che implementa un sistema di riconoscimento visivo di oggetti cubici, detti anche *'blocchi'*, all'interno di una immagine.

Il sistema rappresenta internamente tali oggetti attraverso la costruzione di un modello che ne descrive la disposizione reciproca nella scena.

Quindi è in grado di calcolare una sequenza di azioni che permette virtualmente di disporre gli oggetti secondo uno schema che può essere definito dall'utente stesso.

## **Procedura di riconoscimento**

L'applicazione è in grado di individuare oggetti all'interno di una immagine attraverso la percezione del colore e delle forme degli oggetti stessi.

L'algoritmo implementato utilizza tecniche di *Image Processing* che estraggono dalle immagini le regioni di pixel che rientrano all'interno di intervalli di colore predefiniti (espressi in formato HSV), successivamente analizza tali regioni e riconosce come blocchi reali solo quelle che rispettano vincoli di dimensione, forma e completezza.

Le regioni scartate possono essere rielaborate modificando i parametri di riconoscimento.

![](/app_snapshot/pagina_riconoscimento.jpg)

## **Risoluzione del Problema**

Una volta costruito un modello, l'utente può scegliere di definire una configurazione finale (goal) oppure di utilizzare quella proposta dall'applicazione.

In quest'ultimo caso, l'obiettivo consiste nel disporre tutti i blocchi di uno stesso colore su una stessa pila.

A questo punto l'applicazione formula un problema di **ricerca nello spazio degli stati** e calcola una strategia risolutiva applicando uno degli algoritmi implementati:

- Breadth First Tree Search
- Breadth First Graph Search
- Depth  First  Tree  Search
- Depth First Graph Search
- Iterative  Depth  First  Search
- A*  search

Il *Breadth First Tree Search* è l'opzione di default, tuttavia l'utente può scegliere quale algoritmo utilizzare.

![](/app_snapshot/pagina_modello.jpg)

## **Eseguire il codice**

Step 1: Clonare la repository

```
git clone https://github.com/davide-belfiori/rgblocks_world
cd rgblocks_world
```

Step 2: Eseguire con Python

```
python RGBlocksWorld.py
```
