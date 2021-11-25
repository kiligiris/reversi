import numpy as np
import random
import sys

EMPTY = 0
WHITE = -1
BLACK = 1
WALL  = 2

BOARD_SIZE = 8
HALF_SIZE = int(BOARD_SIZE / 2)

MAX_TURNS = BOARD_SIZE * BOARD_SIZE - 4

# 各方向に対応したインクリメント
DIRECTION = { 
    "left"        : {"x" : -1, "y" : 0},  # 1
    "upper_left"  : {"x" : -1, "y" : -1}, # 2
    "upper"       : {"x" : 0,  "y" : -1}, # 4
    "upper_right" : {"x" : 1,  "y" : -1}, # 8
    "right"       : {"x" : 1,  "y" : 0},  # 16
    "lower_right" : {"x" : 1,  "y" : 1},  # 32
    "lower"       : {"x" : 0,  "y" : 1},  # 64
    "lower_left"  : {"x" : -1, "y" : 1},  # 128
}

IN_ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
IN_NUMBER = ['1', '2', '3', '4', '5', '6', '7', '8']

# 人間の色
if len(sys.argv) >= 2 and (sys.argv[1] == "B" or sys.argv[1] == "W"):
    HUMAN_COLOR = sys.argv[1]
else:
    HUMAN_COLOR = 'B'

# NPC同士の対戦
if len(sys.argv) >= 2 and sys.argv[1] == "c":
    IS_NPC = True
elif len(sys.argv) >= 3 and sys.argv[2] == "c":
    IS_NPC = True
else:
    IS_NPC = False

# プレイヤー同士の対戦
if len(sys.argv) >= 2 and sys.argv[1] == "p":
    IS_PLAYER = True
elif len(sys.argv) >= 3 and sys.argv[2] == "p":
    IS_PLAYER = True
else:
    IS_PLAYER = False

class Board():

    def __init__(self):
        self.RawBoard = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
 
        # 壁の設定
        self.RawBoard[0, :] = WALL
        self.RawBoard[:, 0] = WALL
        self.RawBoard[BOARD_SIZE + 1, :] = WALL
        self.RawBoard[:, BOARD_SIZE + 1] = WALL

        # 初期配置
        self.RawBoard[HALF_SIZE    , HALF_SIZE    ] = WHITE
        self.RawBoard[HALF_SIZE + 1, HALF_SIZE + 1] = WHITE
        self.RawBoard[HALF_SIZE    , HALF_SIZE + 1] = BLACK
        self.RawBoard[HALF_SIZE + 1, HALF_SIZE    ] = BLACK
 
        # 手番
        self.Turns = 0
        self.end_flg = False
        # 現在の手番の色
        self.CurrentColor = BLACK

        if HUMAN_COLOR == 'B':
            self.humanColor = BLACK
        elif HUMAN_COLOR == 'W':
            self.humanColor = WHITE

        # 置ける場所と石が返る方向
        self.MovablePos = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.MovableDir = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
 
        # MovablePosとMovableDirを初期化
        self.initMovable()
    
    def move(self, x, y):
 
        # 置く位置が正しいかどうかをチェック
        if x < 1 or BOARD_SIZE < x:
            return False
        if y < 1 or BOARD_SIZE < y:
            return False
        if self.MovablePos[x, y] == 0:
            return False
 
        # 石を裏返す
        self.flipDiscs(x, y)
        self.Turns += 1
        self.CurrentColor = - self.CurrentColor
        
        # MovablePosとMovableDirの更新
        self.initMovable()

        return True

    def flipDiscs(self, x, y):

        # 石を置く
        self.RawBoard[x, y] = self.CurrentColor

        # 石を裏返す
        dir = self.MovableDir[x, y]

        for i, d in enumerate(DIRECTION):
            if dir & 2 ** i: # 二進数としてAND演算
                self.turnOver(x, y, d)

    def turnOver(self,x ,y ,d):
        x_inc = DIRECTION[d]["x"]
        y_inc = DIRECTION[d]["y"]

        x_tmp = x + x_inc
        y_tmp = y + y_inc

        # 相手の石がある限りひっくり返す
        while self.RawBoard[x_tmp, y_tmp] == - self.CurrentColor:

            self.RawBoard[x_tmp, y_tmp] = self.CurrentColor
            x_tmp += x_inc
            y_tmp += y_inc

    def checkMobility(self, x, y, color):

        # 注目しているマスの裏返せる方向の情報が入る
        dir = 0

        # 既に石がある場合はダメ
        if(self.RawBoard[x, y] != EMPTY):
            return dir

        # 各方向をチェック
        for i, d in enumerate(DIRECTION):
            if self.checkSand(x, y, color, d):
                # 二進数で各方向に対応したflgを立てる
                dir = dir | 2 ** i
        
        return dir

    def checkSand(self, x, y, color, d):
        x_inc = DIRECTION[d]["x"]
        y_inc = DIRECTION[d]["y"]

        x_tmp = x + x_inc
        y_tmp = y + y_inc

        # 直上に相手の石があるか
        if(self.RawBoard[x_tmp, y_tmp] == - color): 
            # 相手の石が続いているだけループ
            while self.RawBoard[x_tmp, y_tmp] == - color:
                x_tmp += x_inc
                y_tmp += y_inc
            
            # 相手の石を挟んで自分の石があればTrueを返す
            if self.RawBoard[x_tmp, y_tmp] == color:
                return True
        
        return False
    
    def initMovable(self):

        self.MovablePos[:, :] = False

        for x in range(1, BOARD_SIZE + 1):
            for y in range(1, BOARD_SIZE + 1):

                # 各マスに置いたときひっくり返せる方向を格納
                dir = self.checkMobility(x, y, self.CurrentColor)
                self.MovableDir[x, y] = dir

                if dir != 0:
                    self.MovablePos[x, y] = True

    def display(self):
 
        print(' a b c d e f g h')
        for y in range(1, 9):

            print(y, end="")
            for x in range(1, 9):

                grid = self.RawBoard[x, y]

                if grid == EMPTY:
                    print('□', end="")
                elif grid == WHITE:
                    print('●', end="")
                elif grid == BLACK:
                    print('〇', end="")

            print()

    def checkIN(self, IN):

        if not IN or len(IN) < 2:
            return False
 
        # INの1文字目と2文字目がそれぞれa~h,1~8の範囲内であるかをチェック
        if IN[0] in IN_ALPHABET:
            if IN[1] in IN_NUMBER:
                return True
 
        return False

    def isGameOver(self):
        if self.end_flg:
            return True

        if self.Turns >= MAX_TURNS:
            return True

        if self.MovablePos.any():
            return False
 
        # 相手に打てる手があった場合はゲームを終了しない
        for x in range(1, BOARD_SIZE + 1):
            for y in range(1, BOARD_SIZE + 1):

                if self.checkMobility(x, y, - self.CurrentColor) != 0:
                    return False
 
        self.gameOver()
        return True

    def gameOver(self):
        self.end_flg = True

    def skip(self):

        # 置くことのできる場所があるならパスできない
        if self.MovablePos.any():
            return False

        if self.isGameOver():
            return False

        self.CurrentColor = - self.CurrentColor
        self.initMovable()

        return True

    def npcInput(self):
        
        # 置けるマス(MovablePos=1)のインデックスをgridsに格納
        grids = np.where(self.MovablePos == 1)

        # 候補からランダムに手を選ぶ
        randam_chosen_index = random.randrange(len(grids[0]))
        x_grid = grids[0][randam_chosen_index]
        y_grid = grids[1][randam_chosen_index]

        # オセロの正式な座標表現で返す
        return IN_ALPHABET[x_grid - 1] + IN_NUMBER[y_grid - 1]
    



if __name__ == "__main__":
    
    board = Board()

    while not board.end_flg:
    
        # 盤面の表示
        board.display()
    
        if board.CurrentColor == BLACK:
            print('黒の番です:', end = "")
        else:
            print('白の番です:', end = "")
    

        if board.CurrentColor == board.humanColor:
            # 先手
            if IS_NPC:
                IN = board.npcInput()
                print(IN)
            else:
                IN = input()
            
        else: # 後手
            if IS_PLAYER:
                IN = input()
            else:
                IN = board.npcInput()
                print(IN)
        print()
        
        # 対戦を終了
        if IN == "exit":
            board.gameOver()
            print('おつかれ')
            break

        # 入力手をチェック
        if board.checkIN(IN):
            x = IN_ALPHABET.index(IN[0]) + 1
            y = IN_NUMBER.index(IN[1]) + 1
        else:
            print('正しい形式(例：f5)で入力してください')
            continue
    
        # 手を打つ
        if not board.move(x, y):
            print('そこには置けません')
            continue

        # 終局判定
        if board.isGameOver():
            board.gameOver()
            print('おわり')
            break

        # パス
        if board.skip():
            print('パスしました')
            print()
            continue

        
    
        

    # ゲーム終了後の表示
    board.display()
    print()
        
    ## 各色の数
    count_black = np.count_nonzero(board.RawBoard[:, :] == BLACK)
    count_white = np.count_nonzero(board.RawBoard[:, :] == WHITE)
        
    print('黒:', count_black)
    print('白:', count_white)
    
    ## 勝敗
    dif = count_black - count_white
    if dif > 0:
        print('黒の勝ち')
    elif dif < 0:
        print('白の勝ち')
    else:
        print('引き分け')