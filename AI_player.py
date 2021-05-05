import datetime
import numpy as np
from board import Board
from copy import deepcopy
import math
import random

class AIPlayer:
    """
    AI玩家
    """
    def UCB1(self, color, board_in):
        board = deepcopy(board_in)
        score_act = None
        act = None
        action_list = list(board.get_legal_actions(color))

        score_sum = 0       # 记录这个节点的总分（用来算select的子节点）

        for action in action_list:
            play_board = deepcopy(board)
            play_board._move(action, color)
            tmp_key = tuple(np.ravel(play_board._board))
            # 计算该action后对应的棋盘的key值
            if self.rec.get((color, tmp_key)):
                # 访问过则继续计算总分
                score_sum += self.rec.get((color, tmp_key))

        for action in action_list:
            play_board = deepcopy(board)
            play_board._move(action, color)
            tmp_key = tuple(np.ravel(play_board._board))
            score_tmp = (self.scr.get((color, tmp_key)) / self.rec.get((color, tmp_key)) + 
                self.C * math.sqrt(
                    math.log(score_sum) / self.rec.get((color, tmp_key))
                ))
            # 计算键值 以及积分
            if score_act == None:
                score_act, act = (score_tmp, action)
            else:
                if score_act < score_tmp:
                    score_act, act = (score_tmp, action)
            # 更新积分最高的子节点
        return act

    def Select(self, board):
        """            
        :param board: 输入需要被搜索的棋盘
        :return: color是select到最后的那个节点已经落子的棋子颜色, act是上一个落子的位置, tmpkey是这个棋盘的状态
        """
        color = self.color
        while(True):
            # 一直select 直到有一个节点没有完全被扩展
            action_list = list(board.get_legal_actions(color))
            if len(action_list) == 0:
                return None, None, None

            all_explored = True # 这个节点的子节点是否全部访问过
            non_vis_son = []    # 记录没有访问过的儿子节点

            score_sum = 0       # 记录这个节点的总分（用来算select的子节点）

            for action in action_list:
                play_board = deepcopy(board)
                play_board._move(action, color)
                tmp_key = tuple(np.ravel(play_board._board))
                # 计算该action后对应的棋盘的key值
                if not self.rec.get((color, tmp_key)):
                    # 没有访问过则记录 该子节点 以及更新节点未访问信息
                    all_explored = False
                    non_vis_son.append((action, tmp_key))
                else:
                    # 访问过则继续计算总分
                    score_sum += self.rec.get((color, tmp_key))

            if all_explored:
                # 如果全部访问过，则在该节点中选择分数最高的儿子
                act = self.UCB1(color, board)
            else:
                # 有未访问节点，则随机返回一个未访问节点，作为extend的对象
                act, tmp_key = (random.choice(non_vis_son))
                board._move(act, color)
                return (color, act, tmp_key)
        
            # 到这里的时候应该是要select下一个节点了
            board._move(act, color)
            tmp_key = tuple(np.ravel(board._board))
            # 落子，更新新棋盘的key值
            self.vis.add((color, tmp_key))
            # 记录路径上的节点信息

            color = "X" if color == "O" else "O"
            # 切换颜色
        

    def game_over(self, board):
        """
        :return: 棋盘上是否还有空位
        """
        b_list = list(board.get_legal_actions('X'))
        w_list = list(board.get_legal_actions('O'))
        return ( len(b_list) == 0 and len(w_list) == 0 )
    
    def Simulate(self, board, player):
        """
        用随机来模拟下棋过程
        :param board: 当前棋盘状态
        :param player: 当前刚完成落子的玩家
        :return: (winner, 分数差), 其中winner是0 黑棋， 1 白棋， 2 平局
        """
        while(True):
            player = "X" if player == "O" else "O"
            # 切换执棋方
            legal_actions = list(board.get_legal_actions(player))
            if len(legal_actions) == 0:
                if self.game_over(board):
                    return board.get_winner()
                    # 0 黑棋， 1 白棋， 2 平局
                    # 后面还有个分数差的参数
                    break 
                else:
                    continue
            
            if len(legal_actions) == 0:
                action = None
            else:
                action = random.choice(legal_actions)
            # 用随机落子来模拟
            if action is None:
                continue
            else:
                board._move(action, player)
                if self.game_over(board):
                    return board.get_winner()

    
    def BackPropogate(self, scr_diff):
        """
        :param scr_diff: 乘上系数的AI与对手的分数差
        """
        for (color, key) in self.vis:
            self.rec[(color, key)] += 1
            if color == self.color:           
            # 如果当前决策节点的颜色是AI的颜色，则加上分差，否则减去分差
                self.scr[(color, key)] += scr_diff
            else:
                self.scr[(color, key)] -= scr_diff

    
    def Expand(self, board, color, act, tmpkey):
        """
        :param board: 当前要扩展的棋盘
        :param color: 当前已经落子的棋子颜色
        :param act: 当前已经落子的位置
        :param tmpkey: 当前棋盘状态
        :return: 返回乘上系数后得到的分差
        """
        game_state, scr_diff = self.Simulate(board, color)
        self.rec[(color, tmpkey)] = 1
        # 记录该节点下的访问次数+1
        if (game_state == 0 and self.color == "O") or (game_state == 1 and self.color == "X"):
            scr_diff = - scr_diff
            # 把scr_diff改成（AI-对方）的分差，可以为负
        scr_diff *= 0.2
        # 加一个系数
        if color == self.color:
            # 如果当前决策节点的颜色是AI的颜色，则加上分差，否则减去分差
            self.scr[(color, tmpkey)] = scr_diff
        else:
            self.scr[(color, tmpkey)] = - scr_diff
        return scr_diff



    def MCTS_choice(self, board_input):
        """
        :param board_input: 输入当前棋盘
        :return: 返回落子坐标
        树的状态节点用rec和scr两个dict来存储，存下了（当前落子方，棋盘状态）：（访问次数，合计分数）的状态
        """
        starttime = datetime.datetime.now()

        count = 0
        while True:                
            count += 1
            currenttime = datetime.datetime.now()

            if (currenttime - starttime).seconds > 3 or count > 1000:
                break 

            board = deepcopy(board_input)
            color = "X" if self.color == "O" else "O"
            # color是对方的颜色
            self.vis = set() 
            # 记录树上搜索过的路径，方便更新

            color, act, tmpkey = self.Select(board) 
            # color是select到最后的那个节点已经落子的棋子颜色
            # act是上一个落子的位置
            # tmpkey是这个棋盘的状态

            if color == None:
                # 如果没有可以落子的地方，进入下一轮尝试
                continue 
            scr_diff = self.Expand(board, color, act, tmpkey)
            # Expand 得到当前扩展节点的分数，并用于bp
            self.BackPropogate(scr_diff)

        print(count)
        return self.UCB1(self.color, board_input)


    def __init__(self, color):
        self.color = color
        self.rec = {} # (player, board._board的tuple形式)， 记录该状态尝试的次数
        self.scr = {} # (player, board._board的tuple形式)， 记录该状态的分数
        self.vis = set()
        self.C = 1.4
    
    def get_move(self, board):
        self.rec = {} 
        self.scr = {} 
        # 清除记录的尝试次数和分数

        action = self.MCTS_choice(board)
        return action