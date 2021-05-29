from pynput.keyboard import Listener, Key
import os
from random import randint
import time


# cd /home/max/python  python3 lab1.py 

board = list(range(1,10))
currPos = [0, 0];
counter = 0;
reservedPos = list();
win = False;
winner = "";
draw = False; 


def check_win(board):
    win_coord = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
    for each in win_coord:
        if board[each[0]] == board[each[1]] == board[each[2]]:
            return board[each[0]]
    return False



def check(board):
        global win, winner, draw;
        if counter > 4:
            tmp = check_win(board)
            if tmp:
                win = True;
                winner = tmp;
        if counter == 9 and win == False:
            draw = True;
            print ("Ничья!")


 


def draw_board(board):
    os.system('clear');
    for i in range(3):
        for j in range(3):
            exit = False;
            if currPos[0] == i and currPos[1] == j and win == False and draw == False:
                print ("|", "*" , "|", end = ""); 
            else:
                for pos in reservedPos:
                    if (pos[0] == i and pos[1] == j):
                        print("|", pos[2], "|", end = "");
                        exit = True;
                if exit: continue;
                print ("|", "_" , "|", end = ""); 
        print("\n")






def take_input(player_token):
    valid = False
    while not valid:
        player_answer = 3 * currPos[0] + currPos[1] + 1;
        player_answer = int(player_answer)
        if player_answer >= 1 and player_answer <= 9:
            if (str(board[player_answer-1]) not in "XO"):
                board[player_answer-1] = player_token
                valid = True
                reservedPos.append([currPos[0], currPos[1], player_token])
            else: 
                print('Это место занято!')
                time.sleep(1);
                return



def on_release(key):
    global counter;
    if key == Key.down:
        currPos[0] += 1;
        if (currPos[0] > 2): currPos[0] = 0;
    elif key == Key.up:  
        currPos[0] -= 1;
        if (currPos[0] < 0): currPos[0] = 2;
    elif key == Key.left:
        currPos[1] -= 1;
        if currPos[1] < 0: currPos[1] = 2;
    elif key == Key.right:
        currPos[1] += 1;
        if currPos[1] > 2: currPos[1] = 0;    
    elif key == Key.enter:
        if counter % 2 == 0:
            take_input("X")
        else:
            take_input("O")
        counter += 1;
    draw_board(board) 
    check(board)
    if win: 
        draw_board(board)
        print("Победил {0}!".format(winner));
        exit(0);
    elif draw:
        draw_board(board);
        print("Ничья!");
        exit(0);





with Listener(
    on_release=on_release) as listener:
    listener.join()



      