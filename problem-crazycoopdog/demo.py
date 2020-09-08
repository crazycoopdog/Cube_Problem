#!/usr/local/bin/python3
import traceback
from inspect import signature
from math import inf, log, log2, trunc
import importlib
import sys

import search
from utils import memoize
from grading.util import print_table

rubric = [
    ('compiles', 55),
    ('allMethods', 10),
    ('2actions', 10),
    ('heuristic', 10),
    ('searchComplete', 5),
    ('search<UCS', 5),
    ('search<A*', 5),
    ('4-7actions', 2),
    ('8-15actions', 2),
    ('16-31actions', 2),
    ('32-63actions', 2),
    ('64+actions', 2),
    ('1-3nodes', 2),
    ('4-15nodes', 2),
    ('16-63nodes', 2),
    ('64-255nodes', 2),
    ('256-1023nodes', 2),
    ('1024-4095nodes', 2),
    ('4096-16383nodes', 2),
    ('16384-655351nodes', 2),
    ('65536+nodes', 2),
]
rNames = [pair[0] for pair in rubric]
rPoints = {pair[0]:pair[1] for pair in rubric}

def add(a, b):
    return sum((a, b))

# accumulation methods
accuMethods = {pair[0]: max for pair in rubric}
accuMethods['allMethods'] = add
accuMethods['heuristic'] = min

def assignFullCredit(sd, key):
    sd[key] = rPoints[key]

def partialCredit(key, minx, maxx, x):
    maxpoints = rPoints[key]
    return max(0,
        min(maxpoints,
            (x-minx) * maxpoints/(maxx-minx)))

def newScores():
    s = {}
    for pair in rubric:
        label = pair[0]
        s[label] = 0
    s['heuristic'] = rPoints['heuristic']
    return s

def scoreList(scores):
    unlabeled = []
    for pair in rubric:
        label = pair[0]
        if label in scores:
            unlabeled.append(scores[label])
        else:
            unlabeled.append(0)
    return unlabeled

comments = []
def addComment(comment):
    global comments
    comments += [comment]

def aAndC(iProblem, goalNode):
    hFun = getattr(iProblem, "h", None)
    if hFun == None:
        return False, False
    pLabel = iProblem.label
    if not callable(hFun):
        addComment("%s.h() is not a function." % pLabel)
        return False, False
    try:
        node = goalNode
        node.h = iProblem.h(node)
        if node.h != 0:
            addComment("%s.h() is not admissible." % pLabel)
            return False, False
        reverse_cost = 0
        path = [node]
        parent = node.parent
        consistent = True
        while parent != None:
            path += [parent]
            parent.h = iProblem.h(parent)
            linkCost = node.path_cost - parent.path_cost
            reverse_cost += linkCost
            if parent.h > reverse_cost:
                addComment("%s.h() is not admissible." % pLabel)
                return False, False
            if parent.h > linkCost + node.h:
                addComment("%s.h() is not consistent." % pLabel)
                consistent = False
            node = parent
            parent = node.parent
        return True, consistent
    except:
        addComment("Heuristic for %s threw this exception:\n" % pLabel
                   + traceback.format_exc())

def gradeProblem(searcher, iProblem, goalNode):
    info = {}
    score = newScores()
    assignFullCredit(score, 'compiles')
    depth = goalNode.path_cost
    if depth < 1 or depth == inf:
        return score
    if searcher in standardSearchList:
        score['allMethods'] = partialCredit(
            'allMethods', 0, len(standardSearchList), 1)
    admissible, consistent = aAndC(iProblem, goalNode)
    sum = admissible + consistent
    score['heuristic'] = partialCredit('heuristic', 0, 2, sum)
    if depth == 2:
        assignFullCredit(score, '2actions')
    elif depth > 2:
        logDepth = trunc(log2(depth))
        minLDI = rNames.index('4-7actions')
        maxLDI = rNames.index('64+actions')
        LDIndex = minLDI + logDepth - 2
        LDIndex = max(minLDI, min(maxLDI, LDIndex))
        lBName = rNames[LDIndex]
        assignFullCredit(score, lBName)
    breadth = iProblem.states
    logBreadth = trunc(log2(breadth)/2)
    minLBI = rNames.index('1-3nodes')
    maxLBI = rNames.index('65536+nodes')
    LBIndex = minLBI + logBreadth - 1
    LBIndex = max(minLBI, min(maxLBI, LBIndex))
    lBName = rNames[LBIndex]
    assignFullCredit(score, lBName)

    info['score'] = score
    return info

def compare_searchers(problems, header, searchers=[]):
    best = {}
    bestNode = {}
    gradeInfo = {}
    for p in problems:
        best[p.label] = inf
        bestNode[p.label] = None
    def do(searcher, problem):
        nonlocal best, bestNode, gradeInfo
        ip = search.InstrumentedProblem(problem)
        try:
            ipLabel = ip.label
            if not ipLabel in gradeInfo:
                gradeInfo[ipLabel] = {}
            goalNode = searcher(ip)
            gradeInfo[ipLabel][searcher] = \
                gradeProblem(searcher, ip, goalNode)
            cost = goalNode.path_cost
            if cost < best[ipLabel]:
                best[ipLabel] = cost
                bestNode[ipLabel] = goalNode
            return ip, cost
        except:
            # print('searcher(' + p.label + ') raised an exception:')
            # traceback.print_exc()
            return ip, inf
    table = [[search.name(s)] + [do(s, p) for p in problems]
             for s in searchers]
    print_table(table, header)
    print('----------------------------------------')
    for p in problems:
        bestPath = []
        node = bestNode[p.label]
        while node != None:
            bestPath.append(node.state)
            node = node.parent
        summary = "Best Path for " + p.label + ": "
        ppFun = getattr(p, "prettyPrint", None)
        if ppFun == None:
            ppFun = str
        ppSep = ' '
        pathLength = len(bestPath)
        if pathLength > 0:
            stateLength = len(ppFun(bestPath[0]))
            if pathLength * stateLength > 100:
                ppSep = "\n"
        for state in reversed(bestPath):
            summary += ppSep + ppFun(state)
        print(summary)
    print('----------------------------------------')
    return gradeInfo

def bestFS(problem, h=None):
    h = memoize(h or problem.h, 'h')
    return search.best_first_graph_search(problem, lambda n: h(n))

def wellFormed(problem):
    if not hasattr( problem, 'initial' ):
        print('iProblem "' + problem.label + '" has no initial state.')
        return False

    if not hasattr(problem, 'actions'):
        print('iProblem "' + problem.label + '" has no actions() method.')
        return False
    pasig = signature(problem.actions)
    if len(pasig.parameters) != 1:
        print('in iProblem "' + problem.label + '",')
        print('  actions(...) has the wrong number of parameters.  Define it as:')
        print('  def actions(self, state):')
        return False

    if not hasattr(problem, 'result'):
        print('iProblem "' + problem.label + '" has no result() method.')
        return False
    prsig = signature(problem.result)
    if len(prsig.parameters) != 2:
        print('in iProblem "' + problem.label + '",')
        print('  result(...) has the wrong number of parameters.  Define it as:')
        print('  def result(self, state, action):')
        return False

    if not hasattr(problem, 'goal_test'):
        if problem.goal == None:
            print('iProblem "' + problem.label + '" has no goal, and no goal_test() method.')
            return False
    pgsig = signature(problem.goal_test)
    if len(pgsig.parameters) != 1:
        print('in iProblem "' + problem.label + '",')
        print('  goal_test(...) has the wrong number of parameters.  Define it as:')
        print('  def goal_test(self, state):')
        return False
    return True

searches = {}
searchMethods = {}
scores = {}

standardSearchList = [
    search.depth_first_graph_search,
    search.breadth_first_search,
    search.iterative_deepening_search,
    search.uniform_cost_search,
    search.astar_search,
]

# Rely on the student to specify appropriate search methods for
# various problems and instances.
baseSearchList=[]

modName = 'instances'

try:
    # http://stackoverflow.com/a/17136796/2619926
    mod = importlib.import_module(modName)
except:
    # print(instances.py is missing or defective.')
    traceback.print_exc()
    sys.exit(1)

roster = mod.names
gradeInfo = {}

for student in roster:
    messages = ['      Searches that compile for %s: ' % (student),
                'Search methods that compile for %s: ' % (student)]
    try:
        searches[student] = mod.searches[student]
        searchLabels = [s.label for s in searches[student]]
        messages[0] += '%s' % (searchLabels)
    except:
        print(student + ': searches[] is missing or defective.')
    try:
        searchMethods[student] = mod.searchMethods[student]
        methodNames = [m.__name__ for m in searchMethods[student]]
        if len(searchMethods[student]) > 0:
            messages[1] += '%s' % (methodNames)
    except:
        print(student + ': searchMethods[] is missing or defective.')

    for m in messages:
        print(m)
    print('----------------------------------------')

    if not student in searches.keys():
        continue
    scores[student] = []
    searchList = [] + baseSearchList
    if student in searchMethods:
        searchList += searchMethods[student]
        # for s in searchMethods[student]:
        #     searchList.append(s)
    try:
        plist = searches[student]
        hlist = [[student],['']]
        i = 0
        for problem in plist:
            if not wellFormed(problem):
                continue
            try:
                hlist[0].append(problem.label)
            except:
                problem.label = 'Problem ' + str(i)
                hlist[0].append(problem.label)
            i += 1
            hlist[1].append('(<succ/goal/stat/fina>, cost)')
        gradeInfo[student] = compare_searchers(
            problems=plist,
            header=hlist,
            searchers=searchList
        )
    except:
        traceback.print_exc()

allScores = newScores()
maxScores = {}
for student in gradeInfo:
    print('Scores for: %s' % student)
    maxScores[student] = {}
    for pLabel in gradeInfo[student]:
        table = []
        maxScores[student][pLabel] = newScores()
        for searcher in gradeInfo[student][pLabel]:
            sLabel = search.name(searcher)
            info = gradeInfo[student][pLabel][searcher]
            scoreSet = info['score']
            table.append(['%s, %s:' % (sLabel, pLabel),
                          scoreList(scoreSet)])
            for label in scoreSet:
                accumulator = accuMethods[label]
                maxScores[student][pLabel][label] = accumulator(
                    maxScores[student][pLabel][label], scoreSet[label])
        if len(table) > 1:
            table.append(['%s summary:' % (pLabel),
                  scoreList(maxScores[student][pLabel])])
        print_table(table)
        if len(table) > 1:
            print()
        for label in allScores:
            allScores[label] = max(allScores[label], maxScores[student][pLabel][label])

realName = mod.names[0]
sl = [int(round(x)) for x in scoreList(allScores)]
print(realName, 'summary:', str(sl))
print(realName, '  total:', str(min(100, sum(sl))))
