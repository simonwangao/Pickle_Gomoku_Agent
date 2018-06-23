from board import *
import time
import random

whoVal = [ 0, 3, 18, 27, 144, 216, 1200, 1800 ]
oppVal = [ 0, 2, 12, 18, 96, 144, 800, 1200 ]

class AI(Board):
    cnt = [ 0 for _ in range(1000) ]    # static member
    def __init__(self):
        super(AI, self).__init__()
        self.total = 0              # 搜索局面数
        self.hashCount = 0          # hash表命中次数
        self.searchDepth = 0        # 实际搜索深度
        self.bestPoint = Point()
        self.bestLine = Line()      # Line
        self.stopThink = False
        self.Npoint = 0
        self.start = 0              # time
    
    def GetTime(self):
        # 返回当前已用的搜索时间(second)
        return time.time() - self.start
    
    def StopTime(self):
        # seconds
        return 30   #change
    
    #@jit
    def ProbeHash(self, depth, alpha, beta):
        # 查询置换表
        phashe = self.hashTable[ self.zobristKey & (hashSize - 1) ]
        if phashe.key == self.zobristKey:
            if phashe.depth >= depth:
                if phashe.hashf == hash_exact:
                    return phashe.val
                elif phashe.hashf == hash_alpha and phashe.val <= alpha:
                    return phashe.val
                elif phashe.hashf == hash_beta and phashe.val >= beta:
                    return phashe.val
        return unknown
    
    #@jit
    def RecordHash(self, depth, val, hashf):
        # 写入置换表
        phashe = self.hashTable[ self.zobristKey & (hashSize - 1) ]
        phashe.key = self.zobristKey
        phashe.val = val
        phashe.hashf = hashf
        phashe.depth = depth
    
    def TurnMove(self, next_):
        # 界面落子
        # next is a Pos
        next_.x += 4
        next_.y += 4
        self.MakeMove(next_)
    
    def gobang(self):
        self.start = time.time()
        self.total = 0
        self.hashCount = 0

        bestMove = Pos()
        if self.step == 0:
            bestMove.x = int(self.size / 2 + 4)
            bestMove.y = int(self.size / 2 + 4)
            return bestMove
        
        if self.step == 1 or self.step == 2:
            flag = True
            rx, ry = 0, 0
            while flag or not self.CheckXy(rx, ry) or self.cell[rx][ry].piece != Empty:
                flag = False
                rx = int(self.remMove[0].x + random.randint(0, self.step * 2) - self.step)
                ry = int(self.remMove[0].y + random.randint(0, self.step * 2) - self.step)
            bestMove.x = rx
            bestMove.y = ry
            return bestMove
        
        # Iterative Deepening Search
        self.stopThink = False
        self.bestPoint.val = 0
        self.IsLose = [ [ False for _ in range(MaxSize+4) ] for _ in range(MaxSize+4) ]
        self.searchDepth = 2
        # don't forget
        while self.searchDepth <= MaxDepth and not self.stopThink:
            self.bestPoint = self.minimax(self.searchDepth, -10001, 10000, self.bestLine)    # main procedure
            if self.stopThink or ( self.searchDepth >= 10 and self.GetTime() >= 1.0 \
                                    and self.GetTime() > self.StopTime() ):
                break
            print (self.searchDepth)    # change
            self.searchDepth += 2
        print (self.searchDepth)
        bestMove = self.bestPoint.p
        return bestMove
    
    def minimax(self, depth, alpha, beta, pline):
        best = self.rootMove[0]
        line = Line()
        line.n = 0

        if depth == 2:
            moves = [ Pos() for _ in range(64) ]
            self.rootCount = self.GetMove(moves)
            if self.rootCount == 1:
                # 只存在一个可行着法，直接返回
                self.stopThink = True
                best.p = moves[0]
                best.val = 0
                pline.n = 0
                return best

            for i in range(self.rootCount):
                self.rootMove[i].p = moves[i]
        else:
            self.sort(self.rootMove, self.rootCount)

        # 遍历可选点
        val = 0
        for i in range(self.rootCount):
            # 搜索非必败点
            p = self.rootMove[i].p
            if not self.IsLose[p.x][p.y]:
                self.MakeMove(p)
                flag = True
                while flag:
                    # pvs
                    flag = False
                    if i > 0 and alpha + 1 < beta:
                        val = -self.AlphaBeta(depth-1, -alpha - 1, -alpha, line)
                        if val <= alpha or val >= beta:
                            break
                    val = -self.AlphaBeta(depth - 1, -beta, -alpha, line)
                self.DelMove()

                self.rootMove[i].val = val

                if self.stopThink:
                    break

                if val == -10000:
                    self.IsLose[p.x][p.y] = True

                if val > alpha:
                    alpha = val
                    best.p = p
                    best.val = val
                    # 保存最佳路线
                    pline.moves[0] = p
                    for j in range(line.n):
                        pline.moves[j+1] = line.moves[j]
                    pline.n = line.n + 1
                    # 找到必胜
                    if val == 10000:
                        self.stopThink = True
                        return best
        return best

    #@autojit
    def MoveNext(self, moveList):
        # 获取下一步着法, moveList is MoveList
        # phase0: 置换表着法
        # phase1: 生成全部着法
        # phase2: 依次返回phase1中的着法
        if moveList.phase == 0:
            moveList.phase = 1
            e = self.pvsTable[ self.zobristKey%pvsSize ]
            if e.key == self.zobristKey:
                moveList.hashMove = e.best
                return e.best
        
        if moveList.phase == 1:
            moveList.phase = 2
            moveList.n = self.GetMove(moveList.moves)
            moveList.index = 0
            if not moveList.first:
                for i in range(moveList.n):
                    if moveList.moves[i].x == moveList.hashMove.x and moveList.moves[i].y == moveList.hashMove.y:
                        for j in range(i+1, moveList.n):
                            moveList.moves[j-1] = moveList.moves[j]
                        moveList.n -= 1
                        break
        
        if moveList.phase == 2:
            if moveList.index < moveList.n:
                moveList.index += 1
                return moveList.moves[ moveList.index - 1 ]
        #else:
        p = Pos()
        p.x = -1
        p.y = -1
        return p
    
    #@autojit
    def RecordPVS(self, best):
        # 记录pv着法, best is Pos
        e = self.pvsTable[ self.zobristKey%pvsSize ]
        e.key = self.zobristKey
        e.best = best

    def AlphaBeta(self, depth, alpha, beta, pline):
        self.total += 1

        self.cnt.pop()  # class variable
        if len(self.cnt) <= 0:
            self.cnt = [ 0 for _ in range(1000) ]
            if self.GetTime() + 0.05 >= self.StopTime():
                # leave a small amount time for dealing other trivial stuff
                self.stopThink = True
                return alpha
        
        if (self.CheckWin()):
            # 对方已成五
            return -10000
        
        if depth <= 0:
            # 叶节点
            return self.evaluate()
        
        # 查询哈希表
        val = self.ProbeHash(depth, alpha, beta)
        if val != unknown:
            self.hashCount += 1
            return val
        
        line = Line()
        line.n = 0
        moveList = MoveList()
        moveList.phase = 0
        moveList.first = True

        p = self.MoveNext(moveList)
        best = Point()
        best.p = p
        best.val = -10000
        hashf = hash_alpha

        while p.x != -1:
            self.MakeMove(p)
            flag = True
            while flag:
                flag = False
                if not moveList.first and alpha + 1 < beta:
                    val = - self.AlphaBeta(depth-1, -alpha-1, -alpha, line)
                    if val <= alpha or val >= beta:
                        break
                val = -self.AlphaBeta(depth-1, -beta, -alpha, line)
            self.DelMove()

            if self.stopThink:
                return best.val
            
            if val >= beta:
                self.RecordHash(depth, val, hash_beta)
                self.RecordPVS(p)
                return val
            
            if val > best.val:
                best.val = val
                best.p = p
                if val > alpha:
                    hashf = hash_exact
                    alpha = val
                    pline.moves[0] = p
                    for j in range(line.n):
                        pline.moves[j+1] = line.moves[j]
                    pline.n = line.n + 1
            
            p = self.MoveNext(moveList)
            moveList.first = False  # not the first child anymore
        
        self.RecordHash(depth, best.val, hashf)
        self.RecordPVS(best.p)

        return best.val
    
    #@autojit
    def CutCand(self, move, cand, candCount):
        # 棋型剪枝
        # move is list of Pos
        # cand is list of Point

        moveCount = 0
        if cand[0].val >= 2400:
            # 存在活四以上的棋形，返回最高分的点
            move[0] = cand[0].p
            moveCount += 1
        elif cand[0].val == 1200:
            # 此时对方存在活三，返回对方活四点和双方冲四点
            move[0] = cand[0].p
            moveCount += 1
            if cand[1].val == 1200:
                move[1] = cand[1].p
                moveCount += 1
            p = Cell()
            if candCount < MaxMoves:
                n = candCount
            else:
                n = MaxMoves
            
            for i in range(moveCount, n):
                p = self.cell[cand[i].p.x][cand[i].p.y]
                if self.IsType(p, self.who, block4) or self.IsType(p, self.opp, block4):
                    move[moveCount] = cand[i].p
                    moveCount += 1
        return moveCount
    
    #@autojit
    def GetMove(self, move):
        # 获取最好的MaxMoves个着法
        # move is a list of Pos
        candCount = 0   # 待选着法数
        moveCount = 0   # 筛选排序后的着法数
        val = 0
        for i in range(self.b_start, self.b_end):
            for j in range(self.b_start, self.b_end):
                if self.cell[i][j].IsCand and self.cell[i][j].piece == Empty:
                    val = self.ScoreMove(self.cell[i][j])
                    if val > 0:
                        self.cand[candCount].p.x = i
                        self.cand[candCount].p.y = j
                        self.cand[candCount].val = val
                        candCount += 1

        self.sort(self.cand, candCount)
        # prune
        moveCount = self.CutCand(move, self.cand, candCount)
        if moveCount == 0:
            # moveCount==0说明没有可以剪枝的特殊情况
            if MaxMoves < candCount:
                moveCount = MaxMoves
            else:
                moveCount = candCount
            for k in range(moveCount):
                move[k] = self.cand[k].p
        return moveCount
    
    #@autojit
    def sort(self, a, n):
        # a is a list of Point
        for i in range(1, n):
            key = a[i]
            j = i
            while j > 0 and a[j-1].val < key.val:
                a[j] = a[j-1]
                j -= 1
            a[j] = key
    
    #@autojit
    def evaluate(self):
        # 局面估值, important
        whoType = [0 for _ in range(8)] # 记录下子方棋形数
        oppType = [0 for _ in range(8)] # 记录另一方棋形数
        block4_temp = 0

        # 统计棋盘所有空点能成的棋形数量
        for i in range(self.b_start, self.b_end):
            for j in range(self.b_start, self.b_end):
                if self.cell[i][j].IsCand and self.cell[i][j].piece == Empty:
                    block4_temp = whoType[block4]
                    self.TypeCount(self.cell[i][j], self.who, whoType)
                    self.TypeCount(self.cell[i][j], self.opp, oppType)
                    # 双冲四等同于活四
                    if whoType[block4] - block4_temp >= 2:
                        whoType[flex4] += 1
        
        # 当前局面轮到who下棋
        # 1.who存在连五点，必胜
        # 2.opp存在两个连五点，无法阻挡，必败
        # 3.opp不能成五，who有活四的空格可下，必胜
        if whoType[win] >= 1:
            return 10000
        if oppType[win] >= 2:
            return -10000
        if oppType[win] == 0 and whoType[flex4] >= 1:
            return 10000
        
        # 计算双方局面分
        whoScore, oppScore = 0, 0
        for i in range(1, 8):
            whoScore += whoType[i] * whoVal[i]
            oppScore += oppType[i] * oppVal[i]
        return whoScore - oppScore
    
    #@autojit
    def ScoreMove(self, c):
        # 着法打分
        score = {}
        score[self.who] = self.pval[ c.pattern[self.who][0] ][ c.pattern[self.who][1] ][ c.pattern[self.who][2] ][ c.pattern[self.who][3] ]
        score[self.opp] = self.pval[ c.pattern[self.opp][0] ][ c.pattern[self.opp][1] ][ c.pattern[self.opp][2] ][ c.pattern[self.opp][3] ]

        # 下子方分值需乘2，因为它的棋形下一手就能形成，而对方的棋形还要下下手
        # 200表示有双活三以上棋形，此时只返回其中更高的一方分值
        # 否则返回双方分值之和
        if score[self.who] >= 200 or score[self.opp] >= 200:
            if score[self.who] >= score[self.opp]:
                return 2 * score[self.who]
            else:
                return score[self.opp]
        else:
            return 2 * score[self.who] + score[self.opp]
    
    def TurnBest(self):
        # 返回最佳点
        best = self.gobang()
        best.x -= 4
        best.y -= 4
        return best


if __name__ == '__main__':
    time0 = time.time()
    a = AI()
    time1 = time.time()
    print (time1 - time0)
