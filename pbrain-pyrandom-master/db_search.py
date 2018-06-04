import random
import time
import copy
import math
from collections import defaultdict
import pisqpipe as pp
import const
import utils

'''
Created by Ao Wang, Github@simonwangao
'''

class Node(object):
    # state: board
    # use operator to change the value on the board
    def __init__(self, node_type=None, level=None, children=None, turn=1, board=None, lastoperator=None):
        self.node_type = node_type
        self.level = level
        self.children = children
        self.turn = turn
        self.board = board
        self.operator = lastoperator    # last operator who change it to the current board (state)

all_nodes = []  # used to record all nodes, remember to clear
all_board_hash = {} # used to store the hash value for fast comparision

def add_dependency_stage(node, level):
    flag = False    # if tree size increased
    if node is not None:
        if level == node.level+1 and ( node.node_type == 'root' or node.node_type == 'combination' ):
            add_dependent_childern(node)
            flag = True
        flag_lis = []
        if node.children is not None:
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
    if node.children is not None:   # test
        raise Exception("Already have childern! In add_dependent_childern")
    node.children = []

    if node.turn == 1:
        operator_lis = const.my_operator_lis    # my turn
    elif node.turn == 2:
        operator_lis = const.opponent_operator_lis  # opponent turn
    
    last_operator = node.operator   # last_operator is actually the key operator, fi
    for operator in operator_lis:
        # operator is an instance of Operator object
        compare_lis = construct_operator_input(node.board, operator.line)
        if compare_lis == operator.pre: # operator is legal:
            if applicable(last_operator, operator): # there is dependency, add new children
                new_board = copy.deepcopy(node.board)
                for pair in operator.add:
                    location, num = pair
                    x, y = location
                    new_board[x][y] = num
                child_node = Node(node_type='dependency', level=node.level+1, turn=3-node.turn, \
                                    board=new_board, lastoperator=operator)
                add_dependent_childern(child_node)
                # note that we may add MORE than a layer of dependent childern

                node_hash_record(child_node)    #record!!!
                node.children.append(child_node)

def possible_node_transfer(node, operator_lis):
    res_dic = {}
    for operator in operator_lis:
        # operator is an instance of Operator object
        compare_lis = construct_operator_input(node.board, operator.line)
        if compare_lis == operator.pre: # operator is legal:
            # doesn't have to be dependency-based
            new_board = copy.deepcopy(node.board)
            for pair in operator.add:
                location, num = pair
                x, y = location
                new_board[x][y] = num
            res_dic[ hash(str(new_board)) ] = (new_board, operator, node)
    return res_dic

def add_combination_stage(node, level, root): # complicated, may be heuristic
    '''
    The combination is exactly two nodes
    node is the current node
    root is the root of the search tree
    '''
    if node.turn == 1:
        operator_lis = const.my_operator_lis    # my turn
    elif node.turn == 2:
        operator_lis = const.opponent_operator_lis  # opponent turn
    
    # don't forget all_nodes!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if node is not None:
        if node.node_type == 'dependency' and node.level = level:
            leaf_nodes = [ leaf_node for leaf_node in all_nodes if len(leaf_node.children) == 0 ]
            for leaf_node in leaf_nodes:    # test node and leaf_node
                if leaf_node.node_type != 'dependency':
                    raise Exception("Wrong in leaf node! In add_combination_stage")
                # possible leaf_node transfer
                leaf_dic = possible_node_transfer(leaf_node, operator_lis)
                current_dic = possible_node_transfer(node, operator_lis)
                inter = [ thing for thing in leaf_dic.keys() if thing in current_dic.keys() ]
                if len(inter) != 0: # have combination
                    for key in inter:
                        new_board, operator1, parent_node1 = leaf_dic[key]
                        new_board, operator2, parent_node2 = current_dic[key]
                        # add new combination node: if there is new operator that depends on both of them
                        


                
                    




def node_hash_record(node):
    all_nodes.append(node)
    all_board_hash[ hash(str(node.board)) ] = node  # record node for combination

nodeType = ['root', 'dependency', 'combination']

tree_size_increased = True  # whether the tree size is increased
def db_search(board):
    level = 1
    root = Node(node_type='root', level=0, turn=1, board=board)  # create root
    all_nodes = []  # clear when start!!!
    all_board_hash = {}
    node_hash_record(root)  # important!!!
    while not pp.terminateAI and tree_size_increased:
        flag1 = add_dependency_stage(root, level)
        flag2 = add_combination_stage(root, level, root)
        level += 1
        if flag1 or flag2:
            tree_size_increased = True
        else:
            tree_size_increased = False
    return None

if __name__ == '__main__':
    pass

