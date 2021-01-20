import sys
import random
import collections
import heapq
import bisect
import time
from copy import deepcopy

nodesE = 0
infile = sys.stdin
lines = infile.readlines()
N = int(lines[0])
graph = []
for x in range(1, N + 1):
    lines[x] = lines[x][:len(lines[x]) - 1]
    graph.append([int(elem) for elem in lines[x].split(", ")])

class PriorityQueue:
    """A Queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first.
    If order is 'min', the item with minimum f(x) is
    returned first; if order is 'max', then it is the item with maximum f(x).
    Also supports dict-like lookup."""
    
    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':  # now item with max f(x)
            self.f = lambda x: -f(x)  # will be popped first
        else:
            raise ValueError("Order must be either 'min' or 'max'.")
        
    def append(self, item):
        """Insert item at its correct position."""
        heapq.heappush(self.heap, (self.f(item), item))
        
    def extend(self, items):
        """Insert each item in items at its correct position."""
        for item in items:
            self.append(item)
            
    def pop(self):
        """Pop and return the item (with min or max f(x) value)
        depending on the order."""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')
        
    def __len__(self):
        """Return current capacity of PriorityQueue."""
        return len(self.heap)
    
    def __contains__(self, key):
        """Return True if the key is in PriorityQueue."""
        return any([item == key for _, item in self.heap])
    
    def __getitem__(self, key):
        """Returns the first value associated with key in PriorityQueue.
        Raises KeyError if key is not present."""
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")
    
    def __delitem__(self, key):
        """Delete the first occurrence of key."""
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)
    
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

    def ex(self, problem):
        if len(self.state[0]) == N + 1:
            return 0
        if len(self.state[0]) == N:
            return problem.path_cost(0, self.state, self.state[2], (self.state[0] + [self.state[2]], self.state[2], self.state[2]))
        edges = []
        for x in range(0, N):
            for y in range(x + 1, N):
                if y not in self.state[0] or x not in self.state[0]:
                    edges.append(problem.path_cost(0, ([x], x, x), y, ([x, y], y, x)))
        return sum(heapq.nsmallest(N - len(self.state[0]), edges))
    
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

def memoize(fn, slot=None, maxsize=32):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, use lru_cache for caching the values."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)
        
    return memoized_fn
    
class TSPProblem(Problem):
    def __init__(self, initial, goal=None):
        super().__init__(initial, goal)
    
    def actions(self, state):
        ret = []
        if len(state[0]) == N:
            return [state[2]];
        for x in range(0, N):
            if x not in state[0]:
                ret.append(x)
        return ret

    def result(self, state, action):
        lst = deepcopy(state[0])
        bisect.insort(lst, action)
        return (lst, action, state[2])

    def goal_test(self, state):
        return len(state[0]) == N + 1

    def path_cost(self, c, state1, action, state2):
        return c + graph[state1[1]][action]

def best_first_graph_search(problem, f, display=False):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = []
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            if display:
                global nodesE
                nodesE = len(explored)
            return node
        explored.append(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None


def A_cheapestEdge(problem, display=False):
    """[Figure 3.14]"""
    return best_first_graph_search(problem, lambda node: (node.path_cost + node.ex(problem)), display)

if __name__ == "__main__":
    t1 = time.process_time()
    t1R = time.time()
    startN = random.randint(0, N - 1)
    UCS = TSPProblem(([startN], startN, startN))
    node = A_cheapestEdge(UCS, True)
    t2 = time.process_time()
    cRun = t2 - t1
    t2R = time.time()
    rRun = t2R - t1R
    filew = open("A_cheapestEdge.csv", "w")
    filew.write("Cost: " + str(node.f) + " Nodes Expanded: " + str(nodesE) + " CPU Runtime: " + str(cRun) + " Real Runtime: " + str(rRun))
    print("Cost: " + str(node.f) + " Nodes Expanded: " + str(nodesE) + " CPU Runtime: " + str(cRun) + " Real Runtime: " + str(rRun))
