from application.blockWorldApp import RGBlocksWorldApplication
from application.appSettings import Settings
from detection.asyncBlockDetector import AsyncBlockDetector
from modelling.solver import AsyncBWPSolver

if __name__ == "__main__":

    try:
        Settings.loadFromFile()
    except:
        print("ATTENZIONE: Errore durante il caricamento delle impostazioni. Verranno utilizzati i parametri di default.")

    blockDetector = AsyncBlockDetector(settings=Settings.propValues(), colors=Settings.COLORS)
    probSolver = AsyncBWPSolver()
    app = RGBlocksWorldApplication(blockDetector, probSolver)
    app.show()