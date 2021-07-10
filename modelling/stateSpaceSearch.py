"""
ATTENZIONE: Parte del contenuto di questo file è stato ripreso della libreria aima-python.

    https://github.com/aimacode/aima-python/blob/master/search.py
"""

import sys
from collections import deque

from modelling.utils import *

class Problem:
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value. Hill Climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError

# ______________________________________________________________________________


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state. Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node. Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action, problem.path_cost(self.path_cost, self.state, action, next_state))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(self.state)


def breadth_first_tree_search(problem, endpoint = None, test_limit = None):
    """
    Search the shallowest nodes in the search tree first.
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Repeats infinitely in case of loops.
    """
    tested = 0
    expanded = 0

    frontier = deque([Node(problem.initial)])  # FIFO queue

    if endpoint != None:
        message = endpoint.receive()
        if message != None and "continue" in message:
            run = message["continue"]
        else: run = True
    else: run = True

    while frontier and run:

        if test_limit != None and tested > test_limit:
            break

        node = frontier.popleft()
        tested += 1

        if problem.goal_test(node.state):
            return node, expanded, tested

        n_exp = node.expand(problem)
        expanded += len(n_exp)
        frontier.extend(n_exp)

        if endpoint != None:
            message = endpoint.receive()
            if message != None and "continue" in message:
                run = message["continue"]

    return None


def depth_first_tree_search(problem, endpoint = None, test_limit = None):
    """
    Search the deepest nodes in the search tree first.
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Repeats infinitely in case of loops.
    """
    tested = 0
    expanded = 0

    frontier = [Node(problem.initial)]  # Stack

    if endpoint != None:
        message = endpoint.receive()
        if message != None and "continue" in message:
            run = message["continue"]
        else: run = True
    else: run = True

    while frontier and run:

        if test_limit != None and tested > test_limit:
            break

        node = frontier.pop()
        tested += 1

        if problem.goal_test(node.state):           
            return node, expanded, tested

        n_exp = node.expand(problem)
        expanded += len(n_exp)
        frontier.extend(n_exp)

        if endpoint != None:
            message = endpoint.receive()
            if message != None and "continue" in message:
                run = message["continue"]

    return None


def depth_first_graph_search(problem, endpoint = None, test_limit = None):
    """
    Search the deepest nodes in the search tree first.
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Does not get trapped by loops.
    If two paths reach a state, only use the first one.
    """
    frontier = [(Node(problem.initial))]  # Stack
    
    tested = 0
    expanded = 0

    if endpoint != None:
        message = endpoint.receive()
        if message != None and "continue" in message:
            run = message["continue"]
        else: run = True
    else: run = True

    explored = set()
    while frontier and run:

        if test_limit != None and tested > test_limit:
            break

        node = frontier.pop()
        tested += 1

        if problem.goal_test(node.state):
            return node, expanded, tested

        explored.add(node.state)

        n_exp = [child for child in node.expand(problem) if child.state not in explored and child not in frontier]
        expanded += len(n_exp)
        frontier.extend(n_exp)

        if endpoint != None:
            message = endpoint.receive()
            if message != None and "continue" in message:
                run = message["continue"]

    return None


def breadth_first_graph_search(problem, endpoint = None, test_limit = None):
    """
    Note that this function can be implemented in a
    single line as below:
    return graph_search(problem, FIFOQueue())
    """
    tested = 0
    expanded = 0

    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node, 1, 0

    frontier = deque([node])
    explored = set()

    if endpoint != None:
        message = endpoint.receive()
        if message != None and "continue" in message:
            run = message["continue"]
        else: run = True
    else: run = True

    while frontier and run:

        if test_limit != None and tested > test_limit:
            break

        node = frontier.popleft()
        explored.add(node.state)

        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                expanded += 1
                if problem.goal_test(child.state):
                    return child, expanded, tested
                frontier.append(child)
                tested += 1

        if endpoint != None:
            message = endpoint.receive()
            if message != None and "continue" in message:
                run = message["continue"]

    return None


def best_first_graph_search(problem, f, endpoint = None, test_limit = None):

    tested = 0
    expanded = 0

    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()

    if endpoint != None:
        message = endpoint.receive()
        if message != None and "continue" in message:
            run = message["continue"]
        else: run = True
    else: run = True

    while frontier and run:

        if test_limit != None and tested > test_limit:
            break

        node = frontier.pop()
        tested += 1

        if problem.goal_test(node.state):
            return node, expanded, tested

        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
                expanded += 1
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)

        if endpoint != None:
            message = endpoint.receive()
            if message != None and "continue" in message:
                run = message["continue"]

    return None



def depth_limited_search(problem, limit=50, endpoint=None, test_limit = None):

    def recursive_dls(node, problem, limit, tested = 0, expanded = 0):

        if test_limit != None and tested > test_limit:
            return 'stop'

        tested += 1
        if problem.goal_test(node.state): 
            return node, expanded, tested
        elif limit == 0:
            return 'cutoff'
        else:

            run = True
            if endpoint != None:
                message = endpoint.receive()
                if message != None and "continue" in message:
                    run = message["continue"]

            if not run:
                return "stop"

            cutoff_occurred = False
            n_exp = node.expand(problem)
            expanded += len(n_exp)
            for child in n_exp:
                result = recursive_dls(child, problem, limit - 1, tested, expanded)
                if result == 'cutoff':
                    cutoff_occurred = True
                elif result is not None:
                    return result
            return 'cutoff' if cutoff_occurred else None

    # Body of depth_limited_search:
    return recursive_dls(Node(problem.initial), problem, limit)


def iterative_deepening_search(problem, endpoint = None, test_limit = None):
    for depth in range(sys.maxsize):
        result = depth_limited_search(problem, depth, endpoint, test_limit=test_limit)
        if result != 'cutoff':
            if result == 'stop':
                return None
            return result


def astar_search(problem, endpoint = None, h=None, test_limit = None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n), endpoint, test_limit)

