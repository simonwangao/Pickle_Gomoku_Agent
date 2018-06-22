from AI import *

pickle = AI()

def toupper(line):
    return line.upper()

def gomocup():
    input_ = Pos()
    best = Pos()
    while(True):
        command = input('Command: ')
        command = toupper(command)
        if command == 'START':  #
            size = input('Size: ')
            pickle.SetSize(size)
            pickle.DisplayBoard()
        elif command == 'RESTART':  #
            pickle.ReStart()
            pickle.DisplayBoard()
        elif command == 'TAKEBACK': #
            pickle.DelMove()
            pickle.DisplayBoard()
        elif command == 'BEGIN':    #Ai开始
            best = pickle.TurnBest()
            pickle.TurnMove(best)
            pickle.DisplayBoard()
        elif command == 'TURN': #
            s = input('Location (separated by SPACE): ')
            s = s.split()
            x, y = int(s[0]), int(s[1])
            tmp = Pos()
            tmp.x, tmp.y = x, y
            pickle.TurnMove(tmp)
            best = pickle.TurnBest()
            pickle.TurnMove(best)
            pickle.DisplayBoard()
        elif command == 'END':
            break



if __name__ == '__main__':
    gomocup()