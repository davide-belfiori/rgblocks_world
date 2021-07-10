from utils.channel import Channel
from modelling.stateSpaceSearch import *
import threading
import time

solver_dict = {
    "Breadth First Tree Search": breadth_first_tree_search,
    "Breadth First Graph Search": breadth_first_graph_search,
    "Depth First Tree Search": depth_first_tree_search,
    "Depth First Graph Search": depth_first_graph_search,
    "Iterative Depth First Search": iterative_deepening_search,
    "A* Search": astar_search
}


class AsyncBWPSolver():

    def __init__(self, problem = None, algorithm = "Breadth First Tree Search", callback = None, test_limit = None) -> None:
        self.problem = problem
        self.algorithm = algorithm
        self.test_limit = test_limit

        self.done_event = threading.Event()
        self.asyncChannel = Channel()
        self.channelClient = self.asyncChannel.registerClient()

        if callback != None:
            self.callback = callback
        else :
            self.callback = lambda s, o : ()

    def setProblem(self, problem):
        self.problem = problem

    def useAlgorithm(self, algorithm):
        self.algorithm = algorithm

    def setCallback(self, callback):
        self.callback = callback

    def setTestLimit(self, test_limit):
        self.test_limit = test_limit

    def isDone(self):
        return self.done_event.is_set()

    def stopSolving(self):
        if not self.isDone():
            self.channelClient.send({"continue" : False})

    def solve(self):
        if self.problem != None:
            solver = solver_dict[self.algorithm]
            solveThread = threading.Thread(target=solve_problem_async, 
                                           args=[self.problem, solver, self.asyncChannel.server, 
                                                 self.done_event, self.callback, self.test_limit])
            self.channelClient.send({"continue":True})
            self.done_event.clear()
            solveThread.start()

    
def solve_problem_async(problem, solver, endpoint, done_event, callback, test_limit):

    start = time.time()
    result = solver(problem = problem, endpoint=endpoint, test_limit = test_limit)
    stop = time.time()
    if result != None:
        done_event.set()
        callback(True, {
            "solution": result[0].path(), 
            "expanded": result[1], 
            "tested": result[2], 
            "time": stop - start
        })
        return

    done_event.set()
    callback(False, {})
    
    