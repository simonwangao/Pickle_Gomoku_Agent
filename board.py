import random
from numba import jit

win = 7             # 连五
flex4 = 6           # 活四
block4 = 5          # 冲四
flex3 = 4           # 活三
block3 = 3          # 眠三
flex2 = 2           # 活二
block2 = 1          # 眠二
Ntype = 8           # 棋型个数
MaxSize = 20        # 棋盘最大尺寸
MaxMoves = 40       # 最大着法数
hashSize = 1 << 22  # 普通置换表尺寸
pvsSize = 1 << 20   # pvs置换表尺寸
MaxDepth = 20       # 最大搜索深度

# 哈希表相关
hash_exact = 0
hash_alpha = 1
hash_beta = 2
unknown = -20000

# 状态相关
Outside = 3
Empty = 0
Me = 1
Opponent = 2

# 方向向量
dx = [ 1, 0, 1, 1 ]
dy = [ 0, 1, 1, -1 ]

class Pos(object):
    def __init__(self):
        self.x = 0
        self.y = 0

class Point(object):
    def __init__(self):
        self.p = Pos()   # Pos
        self.val = 0

class Cell(object):
    def __init__(self):
        self.piece = 0
        self.IsCand = 0
        self.pattern = [ [0 for _ in range(4)] for _ in range(3) ]  # 3 * 4, we only use the second and third layer

class Hashe(object):
    def __init__(self):
        self.key = 0
        self.depth = 0
        self.hashf = 0
        self.val = 0

class Pv(object):
    def __init__(self):
        self.key = 0
        self.best = Pos()   # Pos

class Line(object):
    def __init__(self):
        self.n = 0
        self.moves = [ Pos() for _ in range(MaxDepth) ]  # a list of Pos

class MoveList(object):
    def __init__(self):
        self.phase = 0
        self.n = 0
        self.index = 0
        self.first = False
        self.hashMove = Pos()    # Pos
        self.moves = [ Pos() for _ in range(64) ]    # a list of Pos

class Board(object):
    def __init__(self):
        self.step = 0                                           # 棋盘落子数
        self.size = 20                                          # 棋盘当前尺寸
        self.b_start = 0                                        # 棋盘坐标索引
        self.b_end = 0                                          # 棋盘坐标索引
        self.zobristKey = 0                                     # 表示当前局面的zobristKey
        self.zobrist = [ [ [ 0 for _ in range(MaxSize+4) ] for _ in range(MaxSize+4) ] for _ in range(3) ]   # zobrist键值表
        self.hashTable = [ Hashe() for _ in range(hashSize) ]   # 哈希表, Hashe
        self.pvsTable = [ Pv() for _ in range(pvsSize) ]        # pvs置换表, Pv
        self.typeTable = [ [ [ [ 0 for _ in range(3) ] for _ in range(6) ] for _ in range(6) ] for _ in range(10) ]  # 初级棋型表
        self.patternTable = [ [ 0 for _ in range(3) ] for _ in range(65536) ]    #完整棋型表
        self.pval = [ [ [ [ 0 for _ in range(8) ] for _ in range(8) ] for _ in range(8) ] for _ in range(8) ]    # 棋形分值表
        self.cell = [ [ Cell() for _ in range(MaxSize+8) ] for _ in range(MaxSize+8) ]   # 棋盘
        self.remMove = [ None for _ in range(MaxSize*MaxSize) ]     #记录落子
        self.cand = [ Point() for _ in range(256) ]             # 临时存储合理着法(两格内有子)
        self.IsLose = [ [ False for _ in range(MaxSize+4) ] for _ in range(MaxSize+4) ]  # 记录根节点的必败点
        self.who = Me                                           # 下子方
        self.opp = Opponent                                     # 另一方
        self.rootMove = [ Point() for _ in range(64) ]          # 根节点着法
        self.rootCount = 0                                      # 根节点着法个数

        self.InitType()
        self.InitPattern()
        self.InitPval()
        self.InitZobrist()
        self.SetSize(20)
        # check 1 or 2
    
    def CheckXy(self, x, y):
        # if is ouf of boundary
        return self.cell[x][y].piece != Outside
    
    def LastMove(self):
        return self.cell[ self.remMove[self.step-1].x ][ self.remMove[self.step-1].y ]  # return a cell
    
    def TypeCount(self, c, role, type_lis):
        # c is a cell
        type_lis[ c.pattern[role][0] ] += 1
        type_lis[ c.pattern[role][1] ] += 1
        type_lis[ c.pattern[role][2] ] += 1
        type_lis[ c.pattern[role][3] ] += 1
    
    def IsType(self, c, role, type_num):
        # judge whether the four dorections have the form
        return c.pattern[role][0] == type_num or \
                c.pattern[role][1] == type_num or \
                c.pattern[role][2] == type_num or \
                c.pattern[role][3] == type_num
    
    def CheckWin(self):
        c = self.LastMove()
        return c.pattern[self.opp][0] == win or \
                c.pattern[self.opp][1] == win or \
                c.pattern[self.opp][2] == win or \
                c.pattern[self.opp][3] == win
    
    def Rand64(self):
        return random.randint(0, 1<<64)
    
    def InitZobrist(self):
        for i in range(MaxSize+4):
            for j in range(MaxSize+4):
                self.zobrist[Me][i][j] = self.Rand64()
                self.zobrist[Opponent][i][j] = self.Rand64()

    #@jit
    def SetSize(self, size=20):
        self.size = size
        self.b_start = 4
        self.b_end = size + 4
        for i in range(MaxSize+8):
            for j in range(MaxSize+8):
                if i < 4 or i >= size + 4 or j < 4 or j >= size + 4:
                    self.cell[i][j].piece = Outside
                else:
                    self.cell[i][j].piece = Empty
    
    def MakeMove(self, pos):
        x = pos.x
        y = pos.y

        self.cell[x][y].piece = self.who
        self.zobristKey ^= self.zobrist[self.who][x][y]
        self.who = 3 - self.who # change people
        self.opp = 3 - self.opp
        self.remMove[self.step] = pos
        self.step += 1
        self.UpdateType(x, y)

        for i in range(x-2, x+3):
            self.cell[i][y-2].IsCand += 1
            self.cell[i][y-1].IsCand += 1
            self.cell[i][y  ].IsCand += 1
            self.cell[i][y+1].IsCand += 1
            self.cell[i][y+2].IsCand += 1
    
    def DelMove(self):
        self.step -= 1
        x = self.remMove[self.step].x
        y = self.remMove[self.step].y
        self.who = 3 - self.who # change people
        self.opp = 3 - self.opp
        self.zobristKey ^= self.zobrist[self.who][x][y]
        self.UpdateType(x, y)   # implement later

        for i in range(x-2, x+3):
            self.cell[i][y-2].IsCand -= 1
            self.cell[i][y-1].IsCand -= 1
            self.cell[i][y  ].IsCand -= 1
            self.cell[i][y+1].IsCand -= 1
            self.cell[i][y+2].IsCand -= 1
    
    def Undo(self):
        if self.step >= 2:
            self.DelMove()
            #self.DelMove() #change
        elif step == 1:
            self.DelMove()
    
    def ReStart(self):
        '''
        self.zobristKey = 0
        self.hashTable = [ Hashe() for _ in range(hashSize) ]
        while self.step:
            self.DelMove()
        '''
        self.__init__()
    
    #@jit(nopython=True)
    def UpdateType(self, x, y):
        # 更新棋型
        a = 0
        b = 0
        key = 0

        for i in range(4):
            a = x + dx[i]
            b = y + dy[i]
            j = 0
            while j < 4 and self.CheckXy(a, b):
                key = self.GetKey(a, b, i)
                self.cell[a][b].pattern[Me][i] = self.patternTable[key][Me]
                self.cell[a][b].pattern[Opponent][i] = self.patternTable[key][Opponent]
                # update
                a += dx[i]
                b += dy[i]
                j += 1
            a = x - dx[i]
            b = y - dy[i]

            k = 0
            while k < 4 and self.CheckXy(a, b):
                key = self.GetKey(a, b, i)
                self.cell[a][b].pattern[Me][i] = self.patternTable[key][Me]
                self.cell[a][b].pattern[Opponent][i] = self.patternTable[key][Opponent]
                #update
                a -= dx[i]
                b -= dy[i]
                k += 1
    
    #@jit(nopython=True)
    def GetKey(self, x, y, i):
        # get the key on direction i
        # like encoding
        key = 0
        a = x - dx[i] * 4
        b = y - dy[i] * 4
        for k in range(9):
            if k != 4:
                key <<= 2   # two bits every time
                key ^= self.cell[a][b].piece    # Important! Encode the current location into the key
                # update
                a += dx[i]
                b += dy[i]
                k += 1
        return key
    
    def LineType(self, role, key):
        # like decoding
        line_left = [0 for _ in range(9)]
        line_right = [0 for _ in range(9)]
        for i in range(9):
            if i == 4:
                line_left[i] = role     # notice
                line_right[i] = role    # notice
            else:
                line_left[i] = key & 3  # 3 is b11, we actually get self.cell[a][b].piece in line 243
                line_right[8 - i] = key & 3
                key >>= 2   # two bits
        
        p1 = self.ShortLine(line_left)
        p2 = self.ShortLine(line_right)

        # 同线双四,双三特判
        if p1 == block3 and p2 == block3:
            return self.CheckFlex3(line_left)
        
        if p1 == block4 and p2 == block4:
            return self.CheckFlex4(line_left)
        
        if p1 > p2:
            return p1
        else:
            return p2
    
    #@jit
    def CheckFlex3(self, line):
        # 同线双三特判
        role = line[4]  # real number
        for i in range(9):
            if line[i] == Empty:
                line[i] = role
                type_ = self.CheckFlex4(line)
                line[i] = Empty
                if type_ == flex4:
                    return flex3
        return block3

    #@jit
    def CheckFlex4(self, line):
        # 同线双四特判
        five = 0
        role = line[4]  # real number
        for i in range(9):
            if line[i] == Empty:
                count = 0
                # first round
                j = i - 1
                while j >= 0 and line[j] == role:
                    count += 1
                    j -= 1
                # second round
                j = i + 1
                while j <= 8 and line[j] == role:
                    count += 1
                    j += 1
                if count >= 4:
                    five += 1
        if five >= 2:
            return flex4
        else:
            return block4
    
    #@jit
    def ShortLine(self, line):
        # 判断棋型(单个方向)
        kong = 0
        block = 0
        len1 = 1
        len2 = 1
        count = 1

        who = line[4]   # real number
        for k in range(5, 9):
            if line[k] == who:
                if kong + count > 4:
                    break
                count += 1
                len1 += 1
                len2 = kong + count
            elif line[k] == Empty:
                len1 += 1
                kong += 1
            else:
                if line[k-1] == who:
                    block += 1
                break
        
        # 计算中间空格
        kong = len2 - count
        for k in range(3, -1,-1):
            if line[k] == who:
                if kong + count > 4:
                    break
                count += 1
                len1 += 1
                len2 = kong + count
            elif line[k] == Empty:
                len1 += 1
                kong += 1
            else:
                if line[k+1] == who:
                    block += 1
                break
        return self.typeTable[len1][len2][count][block]
    
    def GetType(self, len1, len2, count, block):
        # 返回对应的棋形
        if len1 >= 5 and count > 1:
            if count == 5:
                return win
            if len1 > 5  and len2 < 5 and block == 0:
                if count == 2:
                    return flex2
                if count == 3:
                    return flex3
                if count == 4:
                    return flex4
            else:
                if count == 2:
                    return block2
                if count == 3:
                    return block3
                if count == 4:
                    return block4
        return 0
    
    def GetPval(self, a, b, c, d):
        # 根据四个方向的棋形打分
        type_ = [ 0 for _ in range(8) ]
        type_[a] += 1
        type_[b] += 1
        type_[c] += 1
        type_[d] += 1

        if type_[win] > 0:
            return 5000
        if type_[flex4] > 0 or type_[block4] > 1:
            return 1200
        if type_[block4] > 0 and type_[flex3] > 0:
            return 1000
        if type_[flex3] > 1:
            return 200
        
        val = [0, 2, 5, 5, 12, 12]
        score = 0
        for i in range(1, block4+1):
            score = score + val[i] * type_[i]
        
        return score

    def InitType(self):
        # 初始化初级棋型表
        for i in range(10):
            for j in range(6):
                for k in range(6):
                    for l in range(3):
                        self.typeTable[i][j][k][l] = self.GetType(i, j, k, l)
    
    def InitPattern(self):
        # 初始化完整棋型表
        for key in range(65536):
            self.patternTable[key][Me] = self.LineType(Me, key)
            self.patternTable[key][Opponent] = self.LineType(Opponent, key)
    
    def InitPval(self):
        # 初始化4个方向组成的棋形分值
        for a in range(8):
            for b in range(8):
                for c in range(8):
                    for d in range(8):
                        self.pval[a][b][c][d] = self.GetPval(a,b,c,d)
    
    def DisplayBoard(self):
        board = [[Empty for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.b_start):
            for j in range(self.b_end):
                board[i-4][j-4] = self.cell[i][j].piece
        
        for i in range(len(board)):
            board[i] = [str(i)] + board[i]

        tmp = [str(i) for i in range(len(board[0]))]
        tmp = ['None'] + tmp
        board = [tmp] + board
        print ('\n')
        for lis in board:
            print (lis)
            print ('\n')

  

        
if __name__ == '__main__':
    import time
    t1 = time.time()
    b = Board()
    t2 = time.time()
    print (t2 - t1)



