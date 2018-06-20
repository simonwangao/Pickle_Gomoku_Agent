import random
import time
import copy
import math
from collections import defaultdict
import pisqpipe as pp
import utils

# define a file for logging ...
DEBUG_LOGFILE = "C:\\Users\\wanga\\Desktop\\pbrain-pickle.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

def logTraceBack():
    import traceback
    with open(DEBUG_LOGFILE,"a") as f:
        traceback.print_exc(file=f)
        f.flush()
    raise

inf = 99999999999999999999999999999999999

class Node:
    def __init__(self, rule = -1, successor = [], value = None, board=None, move=None):
        '''
        -1: min,
        1: max
        move is how parent gets to this node
        '''
        if rule == 1:
            self.rule = 'max'
        else:
            self.rule = 'min'
        self.successor = successor
        self.value = value
        self.board = board
        self.move = move

def node_value(node, alpha, beta):
    if node.rule == 'max':
        return maxValue(node, alpha, beta)
    if node.rule == 'min':
        return minValue(node, alpha, beta)

def maxValue(node, alpha, beta):
    if len(node.successor) == 0:
        #leaf node
        return node.value
    
    v = -inf
    child_list = node.successor
    for child in child_list:
        v = max(v, minValue(child, alpha, beta))
        if v >= beta:
            return v
        alpha = max(v, alpha)
    return v

def minValue(node, alpha, beta):
    if len(node.successor) == 0:
        return node.value
    
    v = inf
    child_list = node.successor
    for child in child_list:
        v = min(v, maxValue(child, alpha, beta))
        if v <= alpha:
            return v
        beta = min(v, beta)
    return v

def get_neighbors(location, board):
    '''
    get the neighbors from the board for one location
    '''
    width = len(board)
    height = len(board[0])

    x, y = location
    start_i = max(x-2, 0)
    end_i = min (x+2, width-1)  # can be reached
    start_j = max(y-2, 0)
    end_j = min (y+2, height-1) # can be reached
    res = [ board[count] for count in range(start_i, end_i+1) ]
    res = [ lis[start_j:end_j+1] for lis in res ]
    return res

def matrix_score(matrix):
    res = [ sum(lis) for lis in matrix ]
    res = sum(res)
    return res 

def construct_tree(height, board, rule, move):
    '''
    important,
    to construct the tree for prune
    rule is a number: 1 or -1
    '''
    #if pp.terminateAI:
        #return -1
    
    width = len(board)
    height = len(board[0])

    child_list = []
    for i in range(width):
        for j in range(height):
            location = (i, j)
            neighbor_matrix = get_neighbors(location, board)
            num = matrix_score(neighbor_matrix)
            if num > 0 and board[i][j] == 0:
                # there are stones in this 5*5 area, accept
                if height == 1:
                    # how to decide value?
                    score = max(utils.my_point_score(location, board), \
                    utils.opponent_point_score(location, board))
                    score = rule * score    # turn to the negative one if necessary
                    changed_board = copy.deepcopy(board)
                    changed_board[i][j] = [ 1 if rule == 1 else 2 ][0]
                    node = Node(rule=-rule, value=score, board=changed_board, move=location)
                    child_list.append(node)
                else:
                    changed_board = copy.deepcopy(board)
                    changed_board[i][j] = [ 1 if rule == 1 else 2 ][0]
                    node = construct_tree(height=height-1, board=changed_board, rule=-rule, move=location)
                    child_list.append(node)
    # temporarily doesn't have value
    root = Node(rule=rule, successor=child_list, board=board, move=move)
    logDebug(str(root.successor))
    return root

def my_turn(board):
    tmp_res = utils.my_move(board)

    width = len(board)
    height = len(board[0])
    # start
    tmp1 = [ sum(lis) for lis in board ]
    tmp2 = sum (tmp1)
    if tmp2 == 0:
        # my first
        x = int(width/2)
        y = int(height/2)
        return (x, y)
    if tmp2 == 2:
        # opponent first
        m = tmp1.index(2)
        row = board[m]
        n = row.index(2)
        lis = [ (m-1,n), (m+1,n), (m,n-1), (m,n+1)] # no diagonal
        feasible = []
        for pair in lis:
            x, y = pair
            if 0<= x < width and 0<= y < height:
                feasible.append( (x, y) )
        return random.choice(feasible)
    
    height = 2
    #try:
    root = construct_tree(height=height, board=board, rule=1, move=None)
    #except:
        #return tmp_res
    root.value = node_value(root, float(-inf), float(inf))

    lis = [ (node.value, node) for node in root.successor ]
    lis.sort(reverse=True)
    res_node = lis[0][1]
    return res_node.move
