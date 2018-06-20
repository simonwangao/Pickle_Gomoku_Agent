import random
import copy
#from collections import defaultdict
#import pisqpipe as pp
import const
import utils

'''
Created by Ao Wang, Github@simonwangao
'''

class Node(object):
    # state: board
    # use operator to change the value on the board
    def __init__(self, node_type=None, level=None, children=[], turn=1, board=None, lastoperator=None):
        self.node_type = node_type
        self.level = level
        self.children = children
        self.turn = turn
        self.board = board
        self.operator = lastoperator    # last operator who change it to the current board (state), a list

all_nodes = []  # used to record all nodes, remember to clear
#all_board_hash = {} # used to store the hash value for fast comparision

def node_hash_record(node):
    all_nodes.append(node)
    all_board_hash[ hash(str(node.board)) ] = node  # record node for combination

def add_dependency_stage(node, level):
    if win_judge(node.board)[0]:
        return False
    
    flag = False    # if tree size increased
    if node is not None:
        if level == node.level+1 and ( node.node_type == 'root' or node.node_type == 'combination' ):
            add_dependent_childern(node)
            flag = True
        flag_lis = []
        if len(node.children) != 0:
            for child in node.children:
                tmp_flag = add_dependency_stage(child, level)
                flag_lis.append(tmp_flag)
        if flag == True or True in flag_lis:
            flag = True
        else:
            flag = False
    return flag

def construct_operator_input(board, line):
    res = []
    for location in line:
        x, y = location
        res.append( (location, board[x][y]) )
    res.sort()
    return tuple(res)

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

def applicable(last_operator, operator):
    '''
    To judge whether the operator is based on the previous one.
    The ESSENCE of dependency-based search
    '''
    inter1 = [ thing for thing in last_operator.add if thing in operator.pre ]
    inter2 = [ thing for thing in last_operator.pre if thing in operator.dele ]
    if len(inter1) != 0 or len(inter2) != 0:
        return True
    else:
        return False

def add_dependent_childern(node):
    if len(node.children) != 0:   # test
        raise Exception("Already have childern! In add_dependent_childern")
    node.children = []

    if node.turn == 1:
        operator_lis = const.my_operator_lis    # my turn
    elif node.turn == 2:
        operator_lis = const.opponent_operator_lis  # opponent turn
    
    last_operator = node.operator   # last_operator is actually the key operator, fi, a list
    for operator in operator_lis:
        # operator is an instance of Operator object
        compare_lis = construct_operator_input(node.board, operator.line)
        if compare_lis == operator.pre: # operator is legal:
            if last_operator is None or applicable(last_operator, operator):
                # notice root node
                new_board = copy.deepcopy(node.board)
                for pair in operator.add:
                    location, num = pair
                    x, y = location
                    new_board[x][y] = num
                child_node = Node(node_type='dependency', level=node.level+1, turn=node.turn, \
                                    board=new_board, lastoperator=operator)
                add_dependent_childern(child_node)
                # note that we may add MORE than a layer of dependent childern

                #node_hash_record(child_node)    #record!!!
                all_nodes.append(child_node)
                node.children.append(child_node)

def board_contain_board(big_board, small_board):
    flag = True
    width = len(small_board)
    height = len(small_board[0])
    for i in range(width):
        for j in range(height):
            if small_board[i][j] != 0:  # consider not-empty part
                if big_board[i][j] != small_board[i][j]:
                    flag = False
                    return flag
    return flag

def not_conflict(node1, node2, operator_lis):   # core problem
    '''
    node1 is the deeper one
    '''
    flag = False
    for operator in operator_lis:
        compare_lis = construct_operator_input(node1.board, operator.line)
        if compare_lis == operator.pre: # operator is legal
            new_board = copy.deepcopy(node1.board)
            for pair in operator.add:
                location, num = pair
                x, y = location
                new_board[x][y] = num
            flag = board_contain_board(new_board, node2.board)
            if flag:
                return flag, operator, new_board
    return flag, None, None

def find_combination_node(partner, node, operator_lis):
    if partner.board == node.board:
        return False
    flag = False    # to judge whether the size is increased
    flag_lis = []
    if node is not None:
        res, last_operator, new_board = not_conflict(partner, node, operator_lis)   # partner is the deeper one
        if res: # no conflict
            if node.node_type == 'dependency':  # judge node type
                for operator in operator_lis:
                    if applicable(last_operator, operator): # if operator exists
                        combination_node = Node(node_type='combination', level=partner.level+1, turn=partner.turn, \
                                                    board=new_board, lastoperator=last_operator)
                        partner.children.append(combination_node)
                        node.children.append(combination_node)

                        #node_hash_record(combination_node)  # record
                        all_nodes.append(combination_node)
                        flag = True # size increased
            
            for child in node.children: # if there is conflict, then there is no need to find node's children
                res = find_combination_node(partner, child, operator_lis)
                flag_lis.append(res)
    if flag or True in flag_lis:
        return True
    else:
        return False

def add_combination_stage(node, level, root): # complicated, may be heuristic
    '''
    The combination is exactly two nodes
    node is the current node
    root is the root of the search tree
    '''
    if win_judge(node.board)[0]:
        return False

    if node.turn == 1:
        operator_lis = const.my_operator_lis    # my turn
    elif node.turn == 2:
        operator_lis = const.opponent_operator_lis  # opponent turn

    flag = False
    flag_lis = []

    if node is not None:
        if node.node_type == 'dependency' and level == node.level:
            flag = find_combination_node(node, root, operator_lis)

        for child in node.children:
            res = add_combination_stage(child, level, root)
            flag_lis.append(res)
    
    if flag or True in flag_lis:
        return True
    else:
        return False

def print_board(board):
    for thing in board:
        print (thing)
    print ('\n')

nodeType = ['root', 'dependency', 'combination']

def db_search(board, turn):
    level = 1
    root = Node(node_type='root', level=0, turn=turn, board=board)  # create root
    all_nodes = []  # clear when start!!!
    #all_board_hash = {}
    #node_hash_record(root)  # important!!!
    all_nodes.append(root)

    tree_size_increased = True  # whether the tree size is increased
    while tree_size_increased:   # not pp.terminateAI and 
        flag1 = add_dependency_stage(root, level)
        flag2 = add_combination_stage(root, level, root)
        level += 1
        if flag1 or flag2:
            tree_size_increased = True
        else:
            tree_size_increased = False
    
    if turn == 1:
        goal_dic = const.my_goal_dic    # my turn
    elif turn == 2:
        goal_dic = const.opponent_goal_dic  # opponent turn
    
    leaf_nodes = [ leaf_node for leaf_node in all_nodes if len(leaf_node.children) == 0 ]

    for leaf_node in leaf_nodes:
        boo, winner = win_judge(leaf_node.board)
        if boo:
            return True, winner # found a threat
    return False, None    # not found

if __name__ == '__main__':
    board =[
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0],
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

    res = db_search(board, 1)
    print (res)

