from random import choice
from copy import deepcopy
from collections import defaultdict
#import pisqpipe as pp

'''
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
'''

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

def get_around_info(board):
    '''
    get the around information in four directions
    for every location in the board
    '''
    width = len(board)
    height = len(board[0])

    dic = {}
    for i in range(width):
        for j in range(height):
            location = (i, j)   # also the key
            res = []

            #row
            start_j = max(j-4, 0)
            end_j = min(height, j+5)
            s = [ str(board[i][temp]) for temp in range(start_j, end_j) ]
            s = ''.join(s)
            if j-4 < 0:
                s = '*'+s   # boundary
            if j+4 >= height:
                s = s+'*'
            res.append(s)

            #column
            start_i = max(0, i-4)
            end_i = min(width, i+5)
            s = [ str(board[temp][j]) for temp in range(start_i, end_i) ]
            s = ''.join(s)
            if i-4 < 0:
                s = '*'+s
            if i+4 >= width:
                s = s+'*'
            res.append(s)

            #left diagonal
            start_i = max(0, i-4)
            end_i = min(width, i+5)
            start_j = max(j-4, 0)
            end_j = min(height, j+5)
            s, x, y = [], start_i, start_j
            while x < end_i and y < end_j:
                s.append( str(board[x][y]) )
                x += 1
                y += 1
            s = ''.join(s)
            if i-4<0 or j-4<0:
                s = '*'+s
            if i+4>=width or j+4>=height:
                s = s+'*'
            res.append(s)

            #right diagonal
            start_i = max(0, i-4)
            end_i = min(width, i+5)
            start_j = min(height-1, j+4)
            end_j = max(j-5, -1)
            s, x, y = [], start_i, start_j
            while x < end_i and y > end_j:
                s.append( str(board[x][y]) )
                x += 1
                y -= 1
            s = ''.join(s)
            if i-4<0 or j+4>=height:
                s = '*'+s
            if i+4>=width or j-4<0:
                s = s+'*'
            res.append(s)
            dic[location] = res
    return dic

def get_point_info(location, board):
    '''
    get the information in four directions
    for one location
    '''
    width = len(board)
    height = len(board[0])
    i, j = location
    res = []

    #row
    start_j = max(j-4, 0)
    end_j = min(height, j+5)
    s = [ str(board[i][temp]) for temp in range(start_j, end_j) ]
    s = ''.join(s)
    if j-4 < 0:
        s = '*'+s   # boundary
    if j+4 >= height:
        s = s+'*'
    res.append(s)

    #column
    start_i = max(0, i-4)
    end_i = min(width, i+5)
    s = [ str(board[temp][j]) for temp in range(start_i, end_i) ]
    s = ''.join(s)
    if i-4 < 0:
        s = '*'+s
    if i+4 >= width:
        s = s+'*'
    res.append(s)

    #left diagonal
    start_i = max(0, i-4)
    end_i = min(width, i+5)
    start_j = max(j-4, 0)
    end_j = min(height, j+5)
    s, x, y = [], start_i, start_j
    while x < end_i and y < end_j:
        s.append( str(board[x][y]) )
        x += 1
        y += 1
    s = ''.join(s)
    if i-4<0 or j-4<0:
        s = '*'+s
    if i+4>=width or j+4>=height:
        s = s+'*'
    res.append(s)

    #right diagonal
    start_i = max(0, i-4)
    end_i = min(width, i+5)
    start_j = min(height-1, j+4)
    end_j = max(j-5, -1)
    s, x, y = [], start_i, start_j
    while x < end_i and y > end_j:
        s.append( str(board[x][y]) )
        x += 1
        y -= 1
    s = ''.join(s)
    if i-4<0 or j+4>=height:
        s = '*'+s
    if i+4>=width or j-4<0:
        s = s+'*'
    res.append(s)
    return res

possible_states = ['win5', 'alive4', 'lian-rush4', 'tiao-rush4', 'lian-alive3', 'tiao-alive3', \
    'lian-sleep3', 'tiao-sleep3', 'te-sleep3', 'jia-alive3', 'alive2', 'sleep2', 'alive1', 'nothreat']

def my_state_string_to_dic(string_lis):
    res = defaultdict(int)  # key is the possible state
    for string in string_lis:
        if '11111' in string:
            res['win5'] += 1
            continue
        if '011110' in string:
            res['alive4'] += 1
            continue
        if '211110' in string or '011112' in string \
            or '*11110' in string or '01111*' in string:
            res['lian-rush4'] += 1
            continue
        if '11101' in string or '10111' in string or '11011' in string:
            res['tiao-rush4'] += 1
            continue
        if '001110' in string or '011100' in string:
            res['lian-alive3'] += 1
            continue
        if '011010' in string or '010110' in string:
            res['tiao-alive3'] += 1
            continue
        if '211100' in string or '001112' in string \
            or '*11100' in string or '00111*' in string:
            res['lian-sleep3'] += 1
            continue
        if '211010' in string or '010112' in string \
            or '*11010' in string or '01011*' in string\
            or '210110' in string or '011012' in string\
            or '*10110' in string or '01101*' in string:
            res['tiao-sleep3'] += 1
            continue
        if '11001' in string or '10011' in string or '10101' in string:
            res['te-sleep3'] += 1
            continue
        if '2011102' in string or '*011102' in string\
            or '201110*' in string or '*01110*' in string:
            res['jia-alive3'] += 1
            continue
        if '001100' in string or '011000' in string\
            or '000110' in string or '001010' in string\
            or '010100' in string or '010010' in string:
            res['alive2'] += 1
            continue
        if '211000' in string or '000112' in string\
            or '*11000' in string or '00011*' in string\
            or '210100' in string or '001012' in string\
            or '*10100' in string or '00101*' in string\
            or '210010' in string or '010012' in string\
            or '*10010' in string or '01001*' in string\
            or '10001' in string or '2010102' in string\
            or '*01010*' in string or '201010*' in string\
            or '*010102' in string or '2011002' in string\
            or '2001102' in string or '*011002' in string\
            or '200110*' in string or '201100*' in string\
            or '*001102' in string:
            res['sleep2'] += 1
            continue
        if '010' in string:
            res['alive1'] += 1
            continue
        res['nothreat'] += 1
    return res

def my_score(res):
    '''
    score = 1100000*res['win5'] + 50000*res['alive4'] + \
                6100*res['lian-rush4'] + 6000*res['tiao-rush4'] + \
                3000*res['lian-alive3'] + 2500*res['tiao-alive3'] + \
                700*res['lian-sleep3'] + 600*res['tiao-sleep3'] + \
                600*res['te-sleep3'] + 600*res['jia-alive3'] + \
                400*res['alive2'] + 300*res['sleep2'] + \
                180*res['alive1'] + 10*res['nothreat']
    '''
    score = 1100000*res['win5'] + 6000*res['alive4'] + \
                5100*res['lian-rush4'] + 5000*res['tiao-rush4'] + \
                4500*res['lian-alive3'] + 4500*res['tiao-alive3'] + \
                3500*res['lian-sleep3'] + 3000*res['tiao-sleep3'] + \
                2800*res['te-sleep3'] + 2800*res['jia-alive3'] + \
                2500*res['alive2'] + 2500*res['sleep2'] + \
                1900*res['alive1'] + 1000*res['nothreat']
    return score

def my_point_score(location, board):
    '''
    location is the place where you (AI) want to put a stone,
    then calculate the score (reward),
    which is the score if AI put the stone in location
    '''
    x, y = location
    if board[x][y] != 0:
        return 0    # if the location is not empty, then the score is 0 
    changed_board = deepcopy(board)
    changed_board[x][y] = 1 # if we put the stone in location

    string_lis = get_point_info(location, changed_board)  # the info strings on four directions
    res = my_state_string_to_dic(string_lis)

    # calculate score using dict res
    score = my_score(res)

    return score

def my_score_matrix(board):
    '''
    to evaluate my current situation
    '''
    width = len(board)
    height = len(board[0])

    string_dic = get_around_info(board)
    score_matrix = [ [0.0 for j in range(height)] for i in range(width) ]
    for i in range(width):
        for j in range(height):
            if board[i][j] == 0:
                location = (i, j)
                score = my_point_score(location, board)
                score_matrix[i][j] = score
            else:
                score_matrix[i][j] = 0

    return score_matrix

def opponent_state_string_to_dic(string_lis):
    res = defaultdict(int)  # key is the possible state
    for string in string_lis:
        if '22222' in string:
            res['win5'] += 1
            continue
        if '022220' in string:
            res['alive4'] += 1
            continue
        if '122220' in string or '022221' in string\
            or '*22220' in string or '02222*' in string:
            res['lian-rush4'] += 1
            continue
        if '22202' in string or '20222' in string or '22022' in string:
            res['tiao-rush4'] += 1
            continue
        if '002220' in string or '022200' in string:
            res['lian-alive3'] += 1
            continue
        if '022020' in string or '020220' in string:
            res['tiao-alive3'] += 1
            continue
        if '122200' in string or '002221' in string\
            or '*22200' in string or '00222*' in string:
            res['lian-sleep3'] += 1
            continue
        if '122020' in string or '020221' in string\
            or '*22020' in string or '02022*' in string\
            or '120220' in string or '022021' in string\
            or '*20220' in string or '02202*' in string:
            res['tiao-sleep3'] += 1
            continue
        if '22002' in string or '20022' in string or '20202' in string:
            res['te-sleep3'] += 1
            continue
        if '1022201' in string or '*022201' in string\
            or '102220*' in string or '*02220*' in string:
            res['jia-alive3'] += 1
            continue
        if '002200' in string or '022000' in string\
            or '000220' in string or '002020' in string\
            or '020200' in string or '020020' in string:
            res['alive2'] += 1
            continue
        if '122000' in string or '000221' in string\
            or '*22000' in string or '00022*' in string\
            or '120200' in string or '002021' in string\
            or '*20200' in string or '00202*' in string\
            or '120020' in string or '020021' in string\
            or '*20020' in string or '02002*' in string\
            or '20002' in string or '1020201' in string\
            or '*02020*' in string or '102020*' in string\
            or '*020201' in string or '1022001' in string\
            or '1002201' in string or '*022001' in string\
            or '100220*' in string or '102200*' in string\
            or '*002201' in string:
            res['sleep2'] += 1
            continue
        if '020' in string:
            res['alive1'] += 1
            continue
        res['nothreat'] += 1
    return res

def opponent_score(res):
    '''
    The corresponding score has to be higher than my_score,
    because the score means that IF we put the stone here
    '''
    '''
    score = 1000000*res['win5'] + 30000*res['alive4'] + \
                7000*res['lian-rush4'] + 6000*res['tiao-rush4'] + \
                2500*res['lian-alive3'] + 2000*res['tiao-alive3'] + \
                800*res['lian-sleep3'] + 700*res['tiao-sleep3'] + \
                700*res['te-sleep3'] + 700*res['jia-alive3'] + \
                500*res['alive2'] + 350*res['sleep2'] + \
                200*res['alive1'] + 10*res['nothreat']
    '''
    score = 1000000*res['win5'] + 7000*res['alive4'] + \
                5300*res['lian-rush4'] + 5200*res['tiao-rush4'] + \
                4700*res['lian-alive3'] +4700*res['tiao-alive3'] + \
                3700*res['lian-sleep3'] + 3200*res['tiao-sleep3'] + \
                3000*res['te-sleep3'] + 3000*res['jia-alive3'] + \
                2600*res['alive2'] + 2600*res['sleep2'] + \
                1900*res['alive1'] + 1000*res['nothreat']
    return score

def opponent_point_score(location, board):
    '''
    location is the place where opponent wants to put a stone,
    then calculate the score (reward),
    which is the score if opponent puts the stone in location
    '''
    x, y = location
    if board[x][y] != 0:
        return 0    # if the location is not empty, then the score is 0 
    changed_board = deepcopy(board)
    changed_board[x][y] = 2 # if opponent puts the stone in location

    string_lis = get_point_info(location, changed_board)  # the info strings on four directions
    res = opponent_state_string_to_dic(string_lis)

    # calculate score using dict res
    score = opponent_score(res)

    return score

def opponent_score_matrix(board):
    '''
    to evaluate opponent's current situation
    '''
    width = len(board)
    height = len(board[0])

    string_dic = get_around_info(board)
    score_matrix = [ [0.0 for j in range(height)] for i in range(width) ]
    for i in range(width):
        for j in range(height):
            if board[i][j] == 0:
                location = (i, j)
                score = opponent_point_score(location, board)
                score_matrix[i][j] = score
            else:
                score_matrix[i][j] = 0
    
    return score_matrix

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
        return choice(feasible)

    # score 
    my_matrix = my_score_matrix(board) # heavy
    opponent_matrix = opponent_score_matrix(board)  # heavy

    my_max = -1
    oppo_max = -1
    for i in range(width):
        for j in range(height):
            # my
            if my_matrix[i][j] >= my_max:
                my_max = my_matrix[i][j]
            # opponent
            if opponent_matrix[i][j] >= oppo_max:
                oppo_max = opponent_matrix[i][j]
    
    my_max_list = []    # locations with max score
    oppo_max_list = []
    for i in range(width):
        for j in range(height):
            # my
            if my_matrix[i][j] == my_max:
                my_max_list.append( (i, j) )    # possible locations
            #opponent
            if opponent_matrix[i][j] == oppo_max:
                oppo_max_list.append( (i, j) )
    
    if my_max > oppo_max:
        # attack
        if len(my_max_list) == 1:
            return my_max_list[0]
        else:
            # my max, opponent max
            lis = [ (opponent_matrix[pair[0]][pair[1]], pair) for pair in my_max_list ] # pair is location
            lis.sort(reverse=True)
            return lis[0][1]    # my max, opponent max location
    else:
        # defence
        if len(oppo_max_list) == 1:
            return oppo_max_list[0]
        else:
            # opponent max, my max
            lis = [ (my_matrix[pair[0]][pair[1]], pair) for pair in oppo_max_list ]
            lis.sort(reverse=True)
            return lis[0][1]
        

