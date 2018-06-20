import random
import copy
#import pisqpipe as pp
import utils

inf = 99999999999999999999999999999999999

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

def max_matrix_score(matrix):
    '''
    the first is the value,
    the second is the location
    '''
    lis1 = [ max(lis) for lis in matrix ]
    max_num = max(lis1)
    row = lis1.index(max_num)
    column = matrix[row].index(max_num)
    return max_num, (row, column)

def final_score(board):
    '''
    the last step is AI
    '''
    width, height = len(board), len(board[0])

    score_matrix1 = utils.my_score_matrix(board)
    score_matrix2 = utils.opponent_score_matrix(board)
    score_lis = []
    for i in range(width):
        for j in range(height):
            max_ = max(score_matrix1[i][j], score_matrix2[i][j])
            min_ = min(score_matrix1[i][j], score_matrix2[i][j])
            score_lis.append( ( max_, min_, (i, j) ) )
    score_lis.sort(reverse=True)
    return score_lis[0][0]

def alpha_beta(layer=None, turn=1, board=None, alpha=-inf, beta=inf, hash_table=None):
    '''
    turn:
        -1: opponent
        1:  me
    '''
    width = len(board)
    height = len(board[0])

    if layer == 1:
        score = final_score(board)
        return score, None  # important
    
    res_lis = []
    score_matrix1 = utils.my_score_matrix(board)
    score_matrix2 = utils.opponent_score_matrix(board)
    score_lis = []
    for i in range(width):
        for j in range(height):
            max_ = max(score_matrix1[i][j], score_matrix2[i][j])
            min_ = min(score_matrix1[i][j], score_matrix2[i][j])
            score_lis.append( ( max_, min_, (i, j) ) )
    score_lis.sort(reverse=True)
    score_lis = score_lis[:10]  #change
    
    if turn == 1:
        for _, _, location in score_lis:
            i, j = location
            neighbor_matrix = get_neighbors(location, board)
            num = matrix_score(neighbor_matrix)
            if num > 0 and board[i][j] == 0:
                #max's turn
                changed_board = copy.deepcopy(board)
                changed_board[i][j] = 1
                score = alpha_beta(layer=layer-1,turn=-turn, board=changed_board, alpha=alpha, beta=beta)[0]
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    return alpha, res_lis
                res_lis.append( (score, location) )
        return alpha, res_lis

    if turn == -1:
        for _, _, location in score_lis:
            i, j = location
            neighbor_matrix = get_neighbors(location, board)
            num = matrix_score(neighbor_matrix)
            if num > 0 and board[i][j] == 0:
                #min's turn
                changed_board = copy.deepcopy(board)
                changed_board[i][j] = 2
                score = alpha_beta(layer=layer-1,turn=-turn, board=changed_board, alpha=alpha, beta=beta)[0]
                if score < beta:
                    beta = score
                if alpha >= beta:
                    return beta, res_lis
                res_lis.append( (score, location) )
        return beta, res_lis

def my_turn(board):
    #tmp_res = utils.my_logd(board)

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
    
    layer = 4

    res = alpha_beta(layer=layer, turn=1, board=board, alpha=-inf, beta=inf)[1]
    res.sort(reverse=True)

    return res[0][1]


if __name__ == '__main__':
    board =[
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    print (my_turn(board))
