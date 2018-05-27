import time
import random
import math
import copy
import pisqpipe as pp

class Board(object):
    '''
    implement mappings between move (a number) and location (a binary tuple)
    '''
    def __init__(self, current_board):
        '''
        current_board is alist of lists
        '''
        self.width = len(current_board)
        self.height = len(current_board[0])
        self.states = {}    #key: move (num), value: player
        self.availables = list( range(self.width*self.height) )
    
    def move_to_location(self, move):
        '''
        3*3 move looks like:
        6 7 8
        3 4 5
        0 1 2
        '''
        h = move  // self.width
        w = move  %  self.width
        return [h, w]
    
    def location_to_move(self, location):
        if(len(location) != 2):
            return -1
        h, w = location
        move = h * self.width + w
        if(move not in range(self.width * self.height)):
            return -1
        return move
    
    def update(self, player, move):
        self.states[move] = player  # num to player
        self.availables.remove(move)

    def current_state(self):
        return tuple((m, self.states[m]) for m in sorted(self.states)) # for hash


class MCTS(object):
    def __init__(self, current_board, time=10, max_actions=1000):
        self.current_board = current_board
        self.time = float(time) # second
        self.max_actions = max_actions

        self.confidence = 1.96
        self.max_depth = 0      #initial
        self.equivalence = 1000

        self.plays = {}         # the number of simulations, key = (action, state)
        self.wins = {}          # the number of win, key = (action, state)
        self.plays_rave = {}    # visited times, key = (move, state)
        self.wins_rave = {}     # {player, win times}, key = (move, state)

        self.play_turn=[0, 1]   # 0:me, 1:opponent
        self.player = self.play_turn[0]

    def get_player(self, players):
        p = players.pop(0)
        players.append(p)
        return p
    
    def adjacent_moves(self, board, state, player, plays):
        """
        adjacent moves without statistics info
        """
        moved = list(set(range(board.width * board.height)) - set(board.availables))
        adjacents = set()
        width = board.width
        height = board.height

        for m in moved:
            h = m // width
            w = m % width
            if w < width - 1:
                adjacents.add(m + 1) # right
            if w > 0:
                adjacents.add(m - 1) # left
            if h < height - 1:
                adjacents.add(m + width) # upper
            if h > 0:
                adjacents.add(m - width) # lower
            if w < width - 1 and h < height - 1:
                adjacents.add(m + width + 1) # upper right
            if w > 0 and h < height - 1:
                adjacents.add(m + width - 1) # upper left
            if w < width - 1 and h > 0:
                adjacents.add(m - width + 1) # lower right
            if w > 0 and h > 0:
                adjacents.add(m - width - 1) # lower left

        adjacents = list(set(adjacents) - set(moved))
        for move in adjacents:
            if plays.get(((move, player), state)):
                adjacents.remove(move)
        return adjacents
    
    def has_a_winner(self, board):
        moved = list(set(range(board.width * board.height)) - set(board.availables))
        if(len(moved) < 5 + 2):
            return False, -1

        width = board.width
        height = board.height
        states = board.states
        n = 5
        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                return True, player

            if (h in range(height - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1
    
    def run_simulation(self, board, play_turn):
        plays = self.plays  # the number of simulation, key = (action, state)
        wins = self.wins
        plays_rave = self.plays_rave
        wins_rave = self.wins_rave
        availables = board.availables

        player = self.get_player(play_turn)
        visited_states = set()
        winner = -1
        expand = True
        states_list = []

        # Simulation
        for t in range(self.max_actions):
            # Selection
            state = board.current_state()
            actions = [ (move, player) for move in availables ]
            # if all moves have info, choose the one with the biggest UCB value
            if all( plays.get((action, state)) for action in actions ):
                total = 0
                for a, s in plays:
                    if s == state:
                        total += plays[(a, s)]
                beta = float(self.equivalence)/(3*total + self.equivalence)

                value, action = max(
                    ( (1-beta) * (float(wins[(action, state)]) / plays[(action, state)]) + 
                    beta * (float(wins_rave[(action[0], state)][player]) / plays_rave[(action[0], state)]) +
                    math.sqrt(float(self.confidence * math.log(total)) / plays[(action, state)]), actions)
                    for action in actions
                )
            else:
                # prefer to choose nearer moves
                adjacents = []
                if len(availables) > 5:
                    adjacents = self.adjacent_moves(board, state, player, plays)

                if len(adjacents):
                    action = (random.choice(adjacents), player)
                else:
                    peripherals = []
                    for action in actions:
                        if not plays.get((action, state)):
                            peripherals.append(action)
                    action = choice(peripherals)
            
            move, p = action
            board.update(player, move)

            # Expand
            if expand and (action, state) not in plays:
                expand = False
                plays[(action, state)] = 0
                wins[(action, state)] = 0

                if t >self.max_depth:
                    self.max_depth = t
            
            states_list.append((action, state))
            for (m, pp), s in states_list:
                if (move, s) not in plays_rave:
                    plays_rave[(move, s)] = 0 
                    wins_rave[(move, s)] = {}              
                    for p in self.play_turn:
                        wins_rave[(move, s)][p] = 0
            
            visited_states.add((action, state))
            is_full = not len(availables)
            win, winner = self.has_a_winner(board)
            if is_full or win:
                break
            
            player = self.get_player(play_turn) #change player

        # Back-propogation
        for i, ((m_root, p), s_root) in enumerate(states_list):
            action = (m_root, p)
            if (action, s_root) in plays:
                plays[(action, s_root)] += 1 # all visited moves
                if player == winner and player in action:
                    wins[(action, s_root)] += 1 # only winner's moves
        
            for ((m_sub, p), s_sub) in states_list[i:]:
                plays_rave[(m_sub, s_root)] += 1 # all child nodes of s_root 
                if winner in wins_rave[(m_sub, s_root)]:                
                    wins_rave[(m_sub, s_root)][winner] += 1 # each node is divided by the player
    
    def prune(self):
        """
        remove not selected path
        """
        length = len(self.current_board.states)
        keys = list(self.plays)
        for a, s in keys:
            if len(s) < length + 2:
                del self.plays[(a, s)]
                del self.wins[(a, s)]

        keys = list(self.plays_rave)
        for m, s in keys:
            if len(s) < length + 2:
                del self.plays_rave[(m, s)]
                del self.wins_rave[(m, s)]
    
    def select_one_move(self):
        """
        select by win percentage 
        """
        percent_wins, move = max(
            (self.wins.get(((move, self.player), self.current_board.current_state()), 0) /
             self.plays.get(((move, self.player), self.current_board.current_state()), 1),
             move)
            for move in self.current_board.availables)
        return move
    
    def get_action(self):
        if len(self.current_board.availables) == 1:
            return self.current_board.availables[0]
        
        simulations = 0
        begin = time.time()
        while pp.terminateAI == 0 and simulations < self.max_actions:  # second, time.time() - begin < self.time
            board_copy = copy.deepcopy(self.current_board)
            play_turn_copy = copy.deepcopy(self.play_turn)
            self.run_simulation(board_copy, play_turn_copy)
            simulations += 1
        
        move = self.select_one_move()
        location = self.current_board.move_to_location(move)
        self.prune()

        return location
