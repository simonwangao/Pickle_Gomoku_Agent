import random
import time
import copy
import math
from collections import defaultdict
import sys
import os
import const

path = sys.path[0]
os.chdir(path)

width, height = 20, 20

def create_G(num):
    res_dic = {}
    for i in range(width):
        for j in range(height):
            #row
            if j + num <= height:
                tup = tuple([ (i, k) for k in range(j, j+num) ])
                res_dic[tup] = 1
            #col
            if i + num <= width:
                tup = tuple([ (k, j) for k in range(i, i+num) ])
                res_dic[tup] = 1
            #left diagonal
            if i + num <= width and j + num <= height:
                tup = tuple([ (i+k, j+k) for k in range(0, num) ])
                res_dic[tup] = 1
            #right diagonal
            if i + num <= width and j - num + 1 >= 0:
                tup = tuple([ (i+k, j-k) for k in range(0, num) ])
                res_dic[tup] = 1
    return res_dic

if __name__ == '__main__':
    # create g5, g6, g7
    pass




