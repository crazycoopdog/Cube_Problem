import search
import random
import sys, traceback

# A trivial Problem definition

class Cube(search.Problem):
    new_cube = '[]'
    new_blueSquare = '@'
    new_blankSquare = ' '
    moves = {
        'right': (0,1),
        'left' : (0, -1),
        'down' : (1, 0),
        'up'   : (-1, 0),
    }
    Game = []
    Game += [new_blueSquare, new_cube]
    print(Game)



'''Left off at creating the cubes physics.'''




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
    'Denning, Cooper',
    'Anderson, Zane',
]

searches = {}
searchMethods = {}

searchMethods[names[0]] = [
    search.depth_first_graph_search,
    search.breadth_first_search,
    search.iterative_deepening_search,
    search.uniform_cost_search,
    search.astar_search,
    flounder,
]

# searches[names[1]] = [
 #   tiles[-6],
  #  tiles[-3],
#]

searchMethods[names[1]] = [
    search.astar_search,
]