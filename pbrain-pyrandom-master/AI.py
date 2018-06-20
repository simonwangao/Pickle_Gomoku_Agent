from board import *
import time

class AI(Board):
    def __init__(self):
        self.total = 0              # 搜索局面数
        self.hashCount = 0          # hash表命中次数
        self.searchDepth = 0        # 实际搜索深度
        self.bestPoint = None       # Point
        self.bestLine = Line        # Line
        self.stopThink = False
        self.Npoint = 0
        self.start = 0              # time
    
    def GetTime(self):
        # 返回当前已用的搜索时间(second)
        return time.time() - self.start()
    
    def StopTime(self):
        # change, 7s
        return 7
    
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
            bestMove.x = self.size / 2 + 4
            bestMove.y = self.size / 2 + 4
            return bestMove
        
        # Iterative Deepening Search
        self.stopThink = False
        self.bestPoint.val = 0
        self.IsLose = [ [ False for _ in range(MaxSize+4) ] for _ in range(MaxSize+4) ]
        self.searchDepth = 2
        # don't forget
        while self.searchDepth <= MaxDepth and not self.stopThink:
            bestPoint = self.minimax(self.searchDepth, -10001, 10000, self.bestLine)    # main procedure
            if self.stopThink or ( self.searchDepth >= 10 and self.GetTime() >= 1.0 \
                                    and self.GetTime() > self.StopTime() ):
                break
            self.searchDepth += 2
        bestMove = self.bestPoint.p
        return bestMove
    
    def minimax(self, depth, alpha, beta, pline):
        pass
        


        
        
        

                








if __name__ == '__main__':
    a = AI()
