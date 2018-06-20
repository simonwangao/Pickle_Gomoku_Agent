import random
import time
import copy
import math
from collections import defaultdict
#import pisqpipe as pp
import utils

'''
Created by Ao Wang, Github@simonwangao
'''

inf = float('inf')

def win_judge(board):
    '''
    to judge whether there is a winner
    '''
    width = len(board)
    height = len(board[0])
    num = 5

    for i in range(width):
        for j in range(height):
            #row
            if j + num <= height:
                tup = tuple([ (i, k) for k in range(j, j+num) ])
                lis = [ board[pair[0]][pair[1]] for pair in tup ]
                res = sum(lis)
                if 0 not in lis and res == 5:
                    return True, 1
                if res == 10:
                    return True, 2
            #col
            if i + num <= width:
                tup = tuple([ (k, j) for k in range(i, i+num) ])
                lis = [ board[pair[0]][pair[1]] for pair in tup ]
                res = sum(lis)
                if 0 not in lis and res == 5:
                    return True, 1
                if res == 10:
                    return True, 2
            #left diagonal
            if i + num <= width and j + num <= height:
                tup = tuple([ (i+k, j+k) for k in range(0, num) ])
                lis = [ board[pair[0]][pair[1]] for pair in tup ]
                res = sum(lis)
                if 0 not in lis and res == 5:
                    return True, 1
                if res == 10:
                    return True, 2
            #right diagonal
            if i + num <= width and j - num + 1 >= 0:
                tup = tuple([ (i+k, j-k) for k in range(0, num) ])
                lis = [ board[pair[0]][pair[1]] for pair in tup ]
                res = sum(lis)
                if 0 not in lis and res == 5:
                    return True, 1
                if res == 10:
                    return True, 2
    return False, None

values = ['true', 'false', 'unknown']
types = ['and', 'or']

class Node(object):
    def __init__(self, proof=-1, disproof=-1, value=None, node_type=None, evaluated=False, \
                    children=[], parent=None, board=None, turn=None, lastmove=None):
        self.proof = proof
        self.disproof = disproof
        self.value = value
        self.node_type = node_type
        self.evaluated = evaluated
        self.children = children
        self.parent = parent
        self.board = board
        self.turn = turn    # used for choosing score matrix in children generation
        self.lastmove = lastmove    # last move to cause current board

def evaluate(node): # heuristic
    if len(node.children) == 0: #leaf node
        boo, winner = win_judge(node.board)
        '''
        if boo:
            for thing in node.board:
                print (thing)
            print ('\n')
        '''
        if boo and winner == 1:
            node.value = 'true' # my
        elif boo and winner == 2:
            node.value = 'false'    # opponent
        elif not boo:
            node.value = 'unknown'
        return
    
    if node.node_type == 'and':
        children_value_lis = [ child.value for child in node.children ]
        if 'false' in children_value_lis:
            node.value = 'false'
        elif 'unknown' in children_value_lis:
            node.value = 'unknown'
        else:
            node.value = 'true'
        return
    
    if node.node_type == 'or':
        children_value_lis = [ child.value for child in node.children ]
        if 'true' in children_value_lis:
            node.value = 'true'
        elif 'unknown' in children_value_lis:
            node.value = 'unknown'
        else:
            node.value = 'false'
        return

def set_proof_and_disproof_numbers(node):
    if node.evaluated:  # inner node
        if node.node_type == 'and':  # and node
            node.proof = 0
            node.disproof = inf
            for child in node.children:
                node.proof += child.proof
                node.disproof = min(node.disproof, child.disproof)
        elif node.node_type == 'or':   # or node
            node.proof = inf
            node.disproof = 0
            for child in node.children:
                node.disproof += child.disproof
                node.proof = min( node.proof, child.proof )
    else:
        if node.value == 'false':
            node.proof = inf
            node.disproof = 0
        elif node.value == 'true':
            node.proof = 0
            node.disproof = inf
        elif node.value == 'unknown':
            node.proof = 1
            node.disproof = 1
    
def select_most_proving_node(node):
    while node.evaluated:
        value = inf
        best = None
        if node.node_type == 'and':
            for child in node.children:
                if value > child.disproof:
                    best = child
                    value = child.disproof
        elif node.node_type == 'or':
            for child in node.children:
                if value > child.proof:
                    best = child
                    value = child.proof
        node = best
    return node

def generate_children(node, num=10):
    '''
    Choose the top num children
    '''
    if len(node.children) != 0:
        raise Exception("Already have childern! In function: generate_children")

    board = copy.deepcopy(node.board)
    score_matrix1 = utils.my_score_matrix(board)
    score_matrix2 = utils.opponent_score_matrix(board)
    
    width, height = len(board), len(board[0])
    score_lis = []
    for i in range(width):
        for j in range(height):
            score_lis.append( (score_matrix1[i][j], (i, j) ) )
            score_lis.append( (score_matrix2[i][j], (i, j) ) )
    score_lis = list(set(score_lis))
    score_lis.sort(reverse=True)
    score_lis = score_lis[:num] #top num

    child_turn = 3 - node.turn
    if child_turn == 1:
        child_type = 'or'
    elif child_turn == 2:
        child_type = 'and'
    
    for _, location in score_lis:
        new_board = copy.deepcopy(board)
        new_board[ location[0] ][ location[1] ] = node.turn #??? it's parent's turn
        child = Node(node_type=child_type, parent=node, board=new_board, turn=child_turn, lastmove=location, children=[])
        node.children.append(child) #problem
        #child.children = [] # can't omit

def expand_node(node):
    generate_children(node)
    for child in node.children:
        evaluate(child)
        set_proof_and_disproof_numbers(child)
        if node.node_type == 'and':
            if child.disproof == 0:
                break
        elif node.node_type == 'or':
            if child.proof == 0:
                break
    node.evaluated = True
        
def update_ancestors(node, root):
    while node is not root:
        old_proof = node.proof
        old_disproof = node.disproof
        set_proof_and_disproof_numbers(node)
        if node.proof == old_proof and node.disproof == old_disproof:
            return node
        node = node.parent
    set_proof_and_disproof_numbers(root)
    return root

def pn_search(board):
    root = Node(node_type='or', board=board, turn=1)
    evaluate(root)
    set_proof_and_disproof_numbers(root)

    current = root
    while root.proof != 0 and root.disproof != 0:   # terminateAI
        most_proving = select_most_proving_node(current)
        expand_node(most_proving)
        current = update_ancestors(most_proving, root)
    if root.proof == 0:
        root.value = 'true'
    elif root.disproof == 0:
        root.value = 'false'
    else:
        root.value = 'unknown'
    return root

def my_move(board):
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
    
    score_matrix1 = utils.my_score_matrix(board)
    score_matrix2 = utils.opponent_score_matrix(board)
    
    score_lis = []
    for i in range(width):
        for j in range(height):
            score_lis.append( (score_matrix1[i][j], (i, j) ) )
            score_lis.append( (score_matrix2[i][j], (i, j) ) )
    score_lis.sort(reverse=True)
    for pair in score_lis:
        new_board = copy.deepcopy(board)
        location = pair[1]
        new_board[location[0]][location[1]] == 1
        node = pn_search(new_board)
        if node.value == 'true':
            return location
    
    return None


if __name__ == '__main__':
    board =[
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    #res = pn_search(board)
    #print (res.value)
    print (my_move(board))

