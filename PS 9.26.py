import numpy as np
import random
import pandas as pd
import time

#初期値を入力
player = 20
basket = 20
hasitem = 0
hasbasket = 0
basketitem = 0
board = [0]*100
save_basket = 0
command = 0
cell = 9
set_state = 51001212

hasitem_max = 2

#↓ シャトルをランダムに配置する
shuttle_pos=random.sample(range(cell*cell),k=10)
num_states = 210000000
num_actions = 6

num_shuttle = 10

# εの設定
epsilon = 1  # εの値を0.1に設定

# Q学習のパラメータ（学習率と割引率）
learning_rate = 0.1
discount_factor = 0.9

basket_reward = 0.2
time_penalty = 0.001

# エピソード数
num_episodes = 10000
time_max = 5000

save_table = []

with open('C:/Users/kd604/Documents/PS/ps.txt', "w") as f:
    f.write("")

#関数
#盤面をコンソールに出力する
def printr(string):
    str1 = string
    for i in range(cell):
        str2 = []
        for e in range(cell):
            str2.append(str1[i*cell+e])
        print(str2)
    print("\n")

#状態数から各パラメータに変換する
def converta(number,shuttle_pos):
    number = number + 1228800000
    numbera = bin(int(str(number)[0:len(str(round(number/100000)))]))[2:]
    shuttle = numbera[3:10+3]
    shuttlea = []
    for i in range(10):
        shuttlea.append(int(shuttle[i]))
    hasitem = int(str(number)[-5])
    hasbasket = int(numbera[-1])
    player = int(str(number)[6:8])
    basket = int(str(number)[8:10])
    board = [0]*(cell*cell)
    e = -1
    for i in shuttlea:
        e = e +1
        if i == 1:
            board[shuttle_pos[e]] = 1
    put_player(player,board)
    put_basket(basket,board)
    return [board,player,basket,hasitem,hasbasket,shuttlea]

#各パラメータから状態数に変換する
def convertb(board,player,basket,hasitem,hasbasket,basketitem,shuttlea):
    numberb = 10
    for i in range(10):
        numberb = numberb*10
        numberb = numberb + shuttlea[i]
    numberb = numberb*10 + hasbasket
    numberb = (int(str(numberb), 2)-12288)*100000
    numberb = numberb + hasitem*10000 + player*100 + basket
    return numberb
  
def output_table(board):
    str1 = board
    str3 = []
    for i in range(cell):
        str2 = []
        for e in range(cell):
            str2.append(str1[i*cell+e])
        str3.append(str2)
    
    str4 = [list(x) for x in zip(str3)]
    
    board = pd.DataFrame(str4)
    print(board)


#ボード上の処理を行う
def put_player(player,board):
  if board[player]==0:board[player]=2
  elif board[player]==1:board[player]=4
  elif board[player]==2:board[player]=2
  elif board[player]==3:board[player]=6
  elif board[player]==4:board[player]=4
  elif board[player]==5:board[player]=7
  elif board[player]==6:board[player]=6
  elif board[player]==7:board[player]=7
  return board

def delete_player(player,board):
  if board[player]==0:board[player]=0
  elif board[player]==1:board[player]=1
  elif board[player]==2:board[player]=0
  elif board[player]==3:board[player]=3
  elif board[player]==4:board[player]=1
  elif board[player]==5:board[player]=5
  elif board[player]==6:board[player]=3
  elif board[player]==7:board[player]=5
  return board

def delete_shuttle(player,board,shuttlea):
  if board[player]==0:board[player]=0
  elif board[player]==1:
      board[player]=1
  elif board[player]==2:
      board[player]=2
  elif board[player]==3:
      board[player]=3
  elif board[player]==4:
      board[player]=2
      shuttlea[shuttle_pos.index(player)] = 0
  elif board[player]==5:
      board[player]=5
  elif board[player]==6:
      board[player]=6
  elif board[player]==7:
      board[player]=6
      shuttlea[shuttle_pos.index(player)] = 0
  
  return [board,shuttlea]

def put_basket(basket,board):
  if basket == 99:
    None
  else:
    if board[basket]==0:board[basket]=3
    elif board[basket]==1:board[basket]=5
    elif board[basket]==2:board[basket]=6
    elif board[basket]==3:board[basket]=3
    elif board[basket]==4:board[basket]=7
    elif board[basket]==5:board[basket]=5
    elif board[basket]==6:board[basket]=6
    elif board[basket]==7:board[basket]=7
  return board

def delete_basket(basket,board):
  if board[basket]==0:board[basket]=0
  elif board[basket]==1:board[basket]=1
  elif board[basket]==2:board[basket]=2
  elif board[basket]==3:board[basket]=0
  elif board[basket]==4:board[basket]=4
  elif board[basket]==5:board[basket]=1
  elif board[basket]==6:board[basket]=2
  elif board[basket]==7:board[basket]=4
  return board


#行動の実行
def action(command,board,player,basket,hasitem,hasbasket,basketitem,shuttlea):
  reward = 0
  if board[player] == 6 or board[player] == 7:
    basketitem = basketitem + hasitem
    reward = reward + 2*hasitem
    hasitem = 0
  if command == 0:
    if player > cell:
      board = delete_player(player,board)
      player = player - cell
      board = put_player(player,board)
  elif command == 1:
    if player%cell != 0 :
      board = delete_player(player,board)
      player = player - 1
      board = put_player(player,board)
  elif command == 2:
    if player < cell*(cell-1) :
      board = delete_player(player,board)
      player = player + cell
      board = put_player(player,board)
  elif command == 3:
    if (player + 1)%cell != 0 :
      board = delete_player(player,board)
      player = player + 1
      board = put_player(player,board)
  elif command == 4:
    if board[player] == 4 or board[player] == 7:
      if hasitem < hasitem_max and hasbasket == 0:#上限
        result = delete_shuttle(player,board,shuttlea)
        board = result[0]
        shuttlea = result[1]
        hasitem = hasitem + 1
        reward = reward + 1
  elif command==5:
    if hasbasket == 0:
      if (board[player] == 6) or (board[player] == 7):
        board = delete_basket(player,board)
        hasbasket = 1
        reward = reward + basket_reward
    else:
      board = put_basket(player,board)
      hasbasket = 0

  if basketitem == 8:
    print("complete")
    reward = reward + 4
  return [board,player,basket,hasitem,hasbasket,basketitem,shuttlea,reward]







# ここからスタート
print('Q-table作成')
# Q-tableの作成
Q = []
for i in range(num_states):
    Q.append([1,1,1,1,1,1])
    if i%2000 == 0:
        print('\r作成中　- ' + str(round(100/num_states*i)) + '%' ,end='')
#Q = [[1 for _ in range(num_actions)] for _ in range(num_states)]
print('作成完了')
print('実行開始')
print('実行中')
# Q学習の実行
for episode in range(num_episodes):
  #初期化
  state = set_state
  timea = 0
  epsilon = epsilon - 1/num_episodes
  if episode%2000 == 0:
      print('\r実行中 - ' + str(round(100/num_episodes*episode)) +'%' ,end='')
  while True:
    timea = timea + 1
    # stateからパラメータに変換
    parameter = converta(state,shuttle_pos)
    board = parameter[0]
    player = parameter[1]
    basket = parameter[2]
    hasitem = parameter[3]
    hasbasket = parameter[4]
    shuttlea = parameter[5]
    
    # ε-greedy法で行動を選択
    if random.uniform(0, 1) < epsilon:
      command = random.randint(0, num_actions - 1)  # εの確率でランダムな行動を選択
    else:
      command = Q[state].index(max(Q[state]))  # 1 - εの確率で最適な行動を選択
    
    #　行動を実行して次の状態と報酬を取得
    next_parameter = action(command,board,player,basket,hasitem,hasbasket,basketitem,shuttlea)  #次の状態
    next_board = next_parameter[0]
    next_player = next_parameter[1]
    next_basket = next_parameter[2]
    next_hasitem = next_parameter[3]
    next_hasbasket = next_parameter[4]
    next_basketitem = next_parameter[5]
    next_shuttlea = next_parameter[6]
    reward = next_parameter[7]
    reward = reward - time_penalty*timea
    
    if hasbasket == 1 and next_hasbasket == 0:
      next_basket = next_player
    
    #次の状態を取得
    next_state = convertb(next_board,next_player,next_basket,next_hasitem,next_hasbasket,next_basketitem,next_shuttlea)

    # Q値の更新（Q学習）
    best_next_action = Q[next_state].index(max(Q[next_state]))
    Q[state][command] = Q[state][command] + learning_rate * (reward + discount_factor * Q[next_state][best_next_action] - Q[state][command])
    
    #状態を進める
    state = next_state
    
    #終了する条件
    if basketitem == 8:
    #( state == num_states - 1:)
      break
    if timea == time_max:
      break
    if next_shuttlea == [0,0,0,0,0,0,0,0] and next_hasitem == 0:
      break

import sys
#sys.exit()



print("学習結果（Qテーブル）:")
#for i in range(num_states):
#  print("状態", i, ":", Q[i])
#for i in range(200):
 # print(Q[next_state-100+i])

# 出力用
state = set_state
timea = 0
save_table.append(converta(state,shuttle_pos)[0])
while True:
  timea = timea + 1
  # stateからパラメータに変換
  parameter = converta(state,shuttle_pos)
  board = parameter[0]
  player = parameter[1]
  basket = parameter[2]
  hasitem = parameter[3]
  hasbasket = parameter[4]
  shuttlea = parameter[5]
  
  # すべてQ-tableに従う
  command = Q[state].index(max(Q[state])) 
  
  #　行動を実行して次の状態と報酬を取得
  next_parameter = action(command,board,player,basket,hasitem,hasbasket,basketitem,shuttlea)  #次の状態
  next_board = next_parameter[0]
  next_player = next_parameter[1]
  next_basket = next_parameter[2]
  next_hasitem = next_parameter[3]
  next_hasbasket = next_parameter[4]
  next_basketitem = next_parameter[5]
  next_shuttlea = next_parameter[6]
  reward = next_parameter[7]
  
  if hasbasket == 1 and next_hasbasket == 0:
    next_basket = next_player
  
  #次の状態を取得
  next_state = convertb(next_board,next_player,next_basket,next_hasitem,next_hasbasket,next_basketitem,next_shuttlea)

  # Q値の更新（Q学習）
  best_next_action = Q[next_state].index(max(Q[next_state]))
  Q[state][command] = Q[state][command] + learning_rate * (reward + discount_factor * Q[next_state][best_next_action] - Q[state][command])
  
  #状態を進める
  state = next_state
  
  #終了する条件
  if basketitem == 8:
  #( state == num_states - 1:)
    break
  if timea == time_max:
    break
  if next_shuttlea == [0,0,0,0,0,0,0,0] and next_hasitem == 0:
    break

  #状態&各パラメータをコンソールに表示
  save_table.append(next_board)

for i in range(len(save_table)):
    output_table(save_table[i])
    time.sleep(0.5)




