import search
import random
import sys, traceback

# A trivial Problem definition
class LightSwitch(search.Problem):
    # initial state constructor inherited

    def actions(self, state):
        return ['up', 'down']

    def result(self, state, action):
        if action == 'up':
            return 'on'
        else:
            return 'off'

    def goal_test(self, state):
        return state == 'on'

switch = LightSwitch('off')
switch.label = 'Light Switch'

class Tile(search.Problem):
    blank = '_'
    moves = {
        'right': ( 0,-1),
        'left' : ( 0, 1),
        'down' : (-1, 0),
        'up'   : ( 1, 0),
    }
    def __init__(self, initial=None, goal=None, moves=10000):
        '''
        Initialize the tile puzzle.
        :param initial: a 2D sequence of characters
        representing tiles on a rectangular board.
        For example, ('123','45_') represents the board:
            1 2 3
            4 5 _
        Each board must contain exactly one _,
        and all other characters must be unique.
        :param goal: another 2D sequence of characters
        containing exactly the same tiles on a board of
        the same dimensions
        '''
        if goal == None:
            raise Exception('A goal must be specified.')
        rg, cg = self.tileCheck(goal)
        self.goal = goal
        self.rows = rg
        self.cols = cg

        if initial == None:
            initial = self.scramble(moves)
            print('initial state: %s' % str(initial))
        else:
            ri, ci = self.tileCheck(initial)
            assert ri == rg
            assert ci == cg

        self.initial = initial

    def actions(self, state):
        row, col = self.findBlank(state)
        actions = []
        if row > 0:
            actions.append('down')
        if col > 0:
            actions.append('right')
        if row < (self.rows - 1):
            actions.append('up')
        if col < (self.cols - 1):
            actions.append('left')
        return actions
        # return self.allowed(row, col)

    def result(self, state, action):
        board = [[t for t in row]
                 for row in state]
        rb, cb = self.findBlank(state)
        rd, cd = self.moves[action]
        rt, ct = rb + rd, cb + cd
        tile = board[rt][ct]
        board[rb][cb] = tile
        board[rt][ct] = self.blank
        newState = tuple([''.join(row)
                          for row in board])
        return newState

    def goal_test(self, state):
        for r in range(self.rows):
            if state[r] != self.goal[r]:
                return False
        return True

    def h(self, node):
        state = node.state
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if state[r][c] == self.blank:
                    continue
                if state[r][c] != self.goal[r][c]:
                    count += 1
        return count

    def findBlank(self, state):
        for r in range(self.rows):
            for c in range(self.cols):
                if state[r][c] == self.blank:
                    return r, c
        raise Exception('%s not found in state: %s' %
              (self.blank, state))

    def tileCheck(self, state):
        try:
            set().add(state)
        except:
            raise Exception(
                'This state is not hashable:\n    %s' % state)
        rows = len(state)
        cols = len(state[0])
        for row in state[1:]:
            assert cols == len(row)
        return rows, cols

    def scramble(self, howMany=10000):
        state = self.goal
        for i in range(howMany):
            actions = self.actions(state)
            children = [self.result(state,a)
                        for a in actions]
            state = random.choice(children)
        return state

tiles = []
tiles += [Tile(('ca','_b'),('ab','c_'))]
tiles[-1].label = '2x2 Tiles, 2 moves'

tiles += [Tile(('dce', '_ba'),('abc','de_'))]
tiles[-1].label = '2x3 Tiles, 10 moves'

tiles += [Tile(('abc', 'e_g', 'dhf'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 8 moves'

tiles += [Tile(('dac','e_f','ghb'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 14 moves'

tiles += [Tile(('_ab', 'dgf', 'ceh'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 16 moves'

tiles += [Tile(('fch','b_g','ead'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 20 moves'

tiles += [Tile(('hgb','dce','af_'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 22 moves'

tiles += [Tile(('ecb', 'h_g', 'dfa'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 24 moves'

tiles += [Tile(('abc', 'd_f', 'geh'), ('abc','def','gh_'))]
tiles[-1].label = '3x3 Tiles, 2 moves'

# moves = 70
# tiles += [Tile(None, ('abc','def','gh_'), moves)]
# tiles[-1].label = '3x3 Tiles, %d moves' % moves

def flounder(problem, giveup=10000):
    'The worst way to solve a iProblem'
    node = search.Node(problem.initial)
    count = 0
    while not problem.goal_test(node.state):
        count += 1
        if count >= giveup:
            return None
        children = node.expand(problem)
        node = random.choice(children)
    return node

# fix this in your first commit and pull
names = [
    'Aardvark, Aaron',
    'Aardvark, Aamy',
]

searches = {}
searchMethods = {}

searches[names[0]] = [
    switch,
    tiles[0],
    tiles[1],
]

searchMethods[names[0]] = [
    search.depth_first_graph_search,
    search.breadth_first_search,
    search.iterative_deepening_search,
    search.uniform_cost_search,
    search.astar_search,
    flounder,
]

searches[names[1]] = [
    tiles[-6],
    tiles[-3],
]

searchMethods[names[1]] = [
    search.astar_search,
]