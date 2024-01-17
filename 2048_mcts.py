# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 08:52:24 2020

@author: 11860
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import copy
import math
import time
import pygame
from pygame.locals import *
import sys

class game:
    def __init__(self,playertype,gui=True):
        self.playertype=playertype
        self.score=0
        self.state=np.array([[0 for i in range(4)] for j in range(4)])
        self.gui=gui
        init=[random.randint(0,15) for i in range(2)]
        while(init[0]==init[1]):
            init[0]=random.randint(0,15)
        for i in init:
            self.state[i//4][i%4]=random.choice([2 for i in range(9)]+[4])
    def right(self,score,generate):  #score 代表记不记分  generate代表生不生成新数字
        for i in range(len(self.state)):
            num=[j for j in self.state[i] if j!=0]
            j=len(num)-1
            while(j>=0):
                if j>=1 and num[j]==num[j-1]:
                    num[j-1]=num[j-1]*2
                    if(score==True):
                        self.score+=num[j-1]
                    num[j]=0
                    j=j-2
                else:
                    j=j-1
            num=[j for j in num if j!=0]
            self.state[i]=[0 for i in range(4-len(num))]+num
        if generate:
            self.generate()
        
    def left(self,score,generate): #score 代表记不记分  generate代表生不生成新数字
        for i in range(len(self.state)):
            num=[j for j in self.state[i] if j!=0]
            num.reverse()
            j=len(num)-1
            while(j>=0):
                if j>=1 and num[j]==num[j-1]:
                    num[j-1]=num[j-1]*2
                    if(score==True):
                        self.score+=num[j-1]
                    num[j]=0
                    j=j-2
                else:
                    j=j-1
            num=[j for j in num if j!=0]
            num.reverse()
            self.state[i]=num+[0 for i in range(4-len(num))]
        if generate:
            self.generate()
    def transpose(self):
        re=[[self.state[i][j] for i in range(4)] for j in range(4)]
        return np.array(re)
    def up(self,score,generate): #score 代表记不记分  generate代表生不生成新数字
        tran=self.transpose()
        self.state=copy.deepcopy(tran)
        self.left(score,generate)
        self.state=copy.deepcopy(self.transpose())
    def down(self,score,generate): #score 代表记不记分  generate代表生不生成新数字
        self.state=copy.deepcopy(self.transpose())
        self.right(score,generate)
        self.state=copy.deepcopy(self.transpose())
    def generate(self):
        emptys=[]
        for i in range(4):
            for j in range(4):
                if self.state[i][j]==0:
                    emptys.append((i,j))
        pos=random.choice(emptys)
        self.state[pos[0]][pos[1]]=random.choice([2 for i in range(13-int(math.log(self.maxnum())))]+[4])
    def legaloperation(self):
        dis=[K_w,K_s,K_a,K_d]
        re=[]
        for di in dis:
            if self.is_valid(di):
                re.append(di)
        return re
    def is_valid(self,di):
        if di==K_w or di==K_s:
            for x in range(4):
                for y in range(4):
                    if( y<3 and self.state[y][x]==self.state[y+1][x] and self.state[y][x]!=0):
                        return True
                    if( di==K_s and y>0 and self.state[y][x]==0 and self.state[y-1][x]!=0 ):
                        return True
                    if(di==K_w and y<3 and self.state[y][x]==0 and self.state[y+1][x]!=0):
                        return True
        if di==K_a or di==K_d:
            for y in range(4):
                for x in range(4):
                    if(x<3 and self.state[y][x]==self.state[y][x+1] and self.state[y][x]!=0):
                        return True
                    if(di==K_d and x>0 and self.state[y][x]==0 and self.state[y][x-1]!=0):
                        return True
                    if(di==K_a and x<3 and self.state[y][x]==0 and self.state[y][x+1]!=0):
                        return True
        return False
    def gameover(self):
        if(len(self.legaloperation())>0):
            return False
        else:
            return True
    def maxnum(self):
        ma=0
        for i in range(4):
            for j in range(4):
                if( self.state[i][j]>ma):
                    ma=self.state[i][j]
        return ma
    def step(self,action):
        if(action==K_w):
            self.up(True,True)
        elif(action==K_s):
            self.down(True,True)
        elif(action==K_a):
            self.left(True,True)
        elif(action==K_d):
            self.right(True,True)
        if(self.gui):
            print(self.state,"\nscore:",self.score)
    def empty(self):
        blank=0
        for i in self.state:
            for j in i:
                if j==0:
                    blank+=1
        return blank
    
class MCTNodes:
    def __init__(self,path,parent,action,state):
        self.path=path+[action]
        self.parent=parent
        self.reward=1
        self.Na=1
        self.UCB=0
        self.children=[]
        self.score=0
        self.state=copy.deepcopy(state)
#        self.state=copy.deepcopy(state)
    def updateUBC(self,Nt):
        if self.Na>0 and Nt>0:
#            print(self.reward/self.parent.reward,math.sqrt( math.log(self.parent.Na)/ self.Na))
            self.UCB=self.reward/self.parent.reward +math.sqrt( math.log(self.parent.Na)/ self.Na)*0.3

class AI:
    def __init__(self,smoothweight,monotoryweight,emptyweight,maxweight,Game):    
        self.smoothweight=smoothweight
        self.monotoryweight=monotoryweight
        self.emptyweight=emptyweight
        self.maxweight=maxweight
        self.Game=Game
    def reward(self,state):
        smoothWeight=self.smoothweight
        monotoryWeight=self.monotoryweight
        emptyWeight=self.emptyweight
        maxWeight=self.maxweight
        def monotory(self,state):
            res=0
            for i in range(4):
                for j in range(3):
                    if state[i][j]<=state[i][j+1]:
                        res+=1
            for j in range(4):
                for i in range(3):
                    if state[i][j]<=state[i+1][j]:
                        res+=1
            return res
        def smooth(self,state):
            res=0
            for i in range(0,3):
                for j in range(0,3):
                    if abs((int(math.log(state[i][j]+1))-int(math.log(state[i][j+1]+1))))<=1 or abs((int(math.log(state[i][j]+1))-int(math.log(state[i+1][j]+1))))<=1:
                           res+=1
            return res
        def empty(self,state):
            res=0
            for i in range(4):
                for j in range(4):
                    if state[i][j]==0:
                        res+=1
        def maxnum(self,state):
            ma=1
            for i in range(4):
                for j in range(4):
                    if state[i][j]>=ma:
                        ma=state[i][j]
            return int(math.log(ma))        
        return smoothWeight*smooth(state)+emptyWeight*empty(state)+monotoryWeight*monotory(state)+maxWeight*maxnum(state)
    
#        #单调性 # It is another heuristic function, you can use line 206~263 to replace the line 173~204.
#        def mono(state):
#            current=state
#            re=0
#            for i in range(4):
#                if(i==0 or i==2):
#                    for j in range(3):
#                        if state[i][j]>=state[i][j+1]:
#                            re+=int(math.log(state[i][j]+1,2))
#                        else:
#                            re-=int(math.log(state[i][j]+1,2))
#                else:
#                    for j in range(3,0,-1):
#                        if state[i][j]>=state[i][j-1]:
#                            re+=int(math.log(state[i][j]+1,2))
#                        else:
#                            re-=int(math.log(state[i][j]+1,2))
#            for j in range(4):
#                for i in range(3):
#                    if(state[i][j]>=state[i+1][j]):
#                        re+=int(math.log(state[i][j]+1,2))
#                    else:
#                        re-=int(math.log(state[i][j]+1,2))
#            return re
#    
#        #平滑性
#        def smooth(state):
#            re=0
#            for i in range(4):
#                for j in range(4):
#                    if(i<3):
#                        re+=abs(int(math.log(state[i][j]+1,2))-int(math.log(state[i+1][j]+1,2)))
#                    if(i>0):
#                        re+=abs(int(math.log(state[i][j]+1,2))-int(math.log(state[i-1][j]+1,2)))
#                    if(j>0):
#                        re+=abs(int(math.log(state[i][j]+1,2))-int(math.log(state[i][j-1]+1,2)))
#                    if(j<3):
#                        re+=abs(int(math.log(state[i][j]+1,2))-int(math.log(state[i][j+1]+1,2)))
#                        
#            return 40-re
#            
#        #空格数
#        def empty(state):
#            re=0
#            for i in range(4):
#                for j in range(4):
#                    if state[i][j]==0:
#                        re+=1
#            return re
#        def maxnum(state):
#            ma=0
#            for i in range(4):
#                for j in range(4):
#                    if( state[i][j]>ma):
#                        ma=state[i][j]
#            return int(math.log(ma+1,2))
##        return smooth(state),empty(state),mono(state)
#        return smoothweight*smooth(state)+emptyweight*empty(state)+monoweight*mono(state)+maxweight*maxnum(state)   
    
    def MCTS(self,state,score):
        root=MCTNodes([],None,None,state)
        root.path=[]
        root.Na=1
        root_state=copy.deepcopy(state)
        root.reward=10
        root.score=score
        nt=1
        iteration_num,iteration_max=0,100
        while iteration_num<iteration_max:
            iteration_num+=1
            now=root
            line=[now]
            #selection
            while True:
                if len(now.children)==0:
                    break
                else:
                    list_UCB=[child.UCB for child in now.children ]
                    max_UCB=max(list_UCB)
                    L=[child for child in now.children if child.UCB==max_UCB]
                    now=random.choice(L)
                    line.append(now)
            #expansion 
            temp_Game=game(2,False)
            temp_Game.state=copy.deepcopy(root.state)
            temp_Game.score=root.score
            if_break=False
            for action in now.path:
                if action in temp_Game.legaloperation():               
                    temp_Game.step(action)
                else:
                    if_break=True
                    break
            if if_break:
                pass
            if not temp_Game.gameover():
                L=temp_Game.legaloperation()
                save_state=copy.deepcopy(temp_Game.state)
                save_score=temp_Game.score
                save_score=0
                for operation in L:
                    temp_Game.state=copy.deepcopy(save_state)
                    temp_Game.score=save_score
                    temp_Game.step(operation)
                    new=MCTNodes(now.path,now,operation,temp_Game.state)
                    now.children.append(new)
                #simulation
                    max_depth=10
                    depth=0
                    while depth<max_depth and (not temp_Game.gameover()):
                        depth+=1
                        operations=temp_Game.legaloperation()
                        if( len(operations)!=0):
                            action=random.choice(operations)
                        else:
                            break
                        temp_Game.step(action)
                    score=temp_Game.score
#                    print(score)
                    if score==0:
                        pass
                    new.Na+=1
                    new.reward=(new.reward*(new.Na-1)+score)/new.Na
                    nt+=1
                    new.updateUBC(nt)
                    #backpropagation
                    for pre in line:
                        pre.Na+=1
                        pre.reward=(pre.reward*(pre.Na-1)+score)/pre.Na
                        if(pre!=root):
                            pre.updateUBC(nt)
            else:
                nt+=1
        max_UCB=-999999
        best_di=None
        for i in root.children:
            if i.UCB>max_UCB:
               best_di=i.path[0]
               max_UCB=i.UCB
        return best_di 
    
class visual:
    def __init__(self):
        self.block=100
        self.inter=10
        self.length=4*self.block+5*self.inter
        self.height=4*self.block+4*self.inter+100
        self.title=pygame.Rect(0,0,self.length,100) 
        self.screen=pygame.display.set_mode((self.length,self.height))
       
    def colors(self,num):
        if num==0:
            return (150,150,150)
        n=math.log(num,2)
        if num<=8:
            return (255,255,255-n*80)
        return (255,255-n*20,50)
    def choose_model(self):
        pygame.font.init()
        font=pygame.font.SysFont("Arial",40)
        font.set_bold(True)
        word=font.render("Person: 1   AI: 2",True,(255,30,50))
        w,h=font.size(str("Person: 1   AI: 2"))
        self.screen.blit(word,(self.length/2-w/2,self.height/2-h/2))

    def cur_state(self,curstate,score):
        pygame.font.init()
        pygame.draw.rect(self.screen,(230,230,230),self.title)
        font = pygame.font.SysFont("Arial", 25)
        self.screen.blit(font.render('Score:', 1, (0,0,255)),(175,50))
        self.screen.blit(font.render('%s'% score, 1, (0,0,255)),(250,50))
        for i in range(4):
            for j in range(4):
                location=[i*self.block+self.inter*(i+1)+100,j*self.block+self.inter*(j+1)]
                pygame.draw.rect(self.screen,self.colors(curstate[i][j]),(location[1],location[0],100,100))
                if curstate[i][j]!= 0:
                    image=font.render(str(int(curstate[i][j])),True,(0,0,0))
                    word_wid,word_he=font.size(str(int(curstate[i][j])))
                    self.screen.blit(image,(location[1]+(100-word_wid)/2,location[0]+(100-word_he)/2))
    def game_over(self,result):
        if result==True:
            pygame.font.init()
            font=pygame.font.SysFont("Arial",60)
            word=font.render("GAME OVER",True,(255,0,255))
            word_wid,word_he=font.size("GAME OVER")
            self.screen.blit(word,(self.length/2-word_wid/2,self.height/2-word_he/2))
    def if_continue(self):
        pygame.font.init()
        font1=pygame.font.SysFont("Arial",30)
        font2=pygame.font.SysFont("Arial",40)
        font3=pygame.font.SysFont("Arial",40)
        font2.set_bold(True)
        font1.set_bold(True)
        font3.set_bold(True)
        word1=font1.render("whether you want to continue?",True,(255,30,50))
        word3=font3.render("You win!",True,(255,30,50))
        word2=font2.render("Yes-1   No-2",True,(255,30,50))
        w1,h1=font1.size(str("whether you want to continue?"))
        w2,h2=font2.size(str("Yes-1   No-2"))
        w3,h3=font3.size(str("You win!"))
        self.screen.blit(word1,(self.length/2-w1/2,self.height/2-h1/2))
        self.screen.blit(word2,(self.length/2-w2/2,3*self.height/4-h2/2))
        self.screen.blit(word3,(self.length/2-w3/2,3*self.height/4-h3/2-200))

def main():
    pygame.init()
    a=visual()
    a.cur_state([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],0)
    a.choose_model()
    pygame.display.update()
    begin=True
    while begin:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)    
            elif event.type == pygame.KEYDOWN:
                if (event.key==K_1):
                    playertype='1'
                    begin=False
                if (event.key==K_2):
                    playertype='2'
                    begin=False
    Game=game(playertype,False)
    ai=AI(1,2,3,4,Game)
    a.__init__()
    a.cur_state([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],0)
    pygame.display.update()
    judge=True
    if playertype=='1':
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)    
                elif event.type == pygame.KEYDOWN:
                    if  (event.key in Game.legaloperation()):
                        Game.step(event.key)
                        state=copy.deepcopy(Game.state)
                        score=Game.score
                        a.cur_state(state,score)
                    elif(event.key==K_e):
                        a.game_over(True)
                        pygame.display.update()
                        break
                if(Game.gameover()):
                    a.game_over(True)
                    pygame.display.update()
                    break
                if Game.state.max()==2048:
                    while judge:
                      a.if_continue()
                      pygame.display.update()
                      for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit(0)
                        elif event.type==pygame.KEYDOWN:
                            if event.key==K_1:
                                judge=False
                                a.__init__()
                                a.cur_state(state,score)
                            if event.key==K_2:
                                a.__init__()
                                a.cur_state(state,score)
                                a.game_over(True)
                        pygame.display.update()
                pygame.display.update()
    if playertype=='2':
        while True:
            smoothweight,monotoryweight,emptyweight,maxweight=20,2,8,10
            if(Game.empty()<2):
                smoothweight,monotoryweight,emptyweight,maxweight=20,2,30,10
            di=ai.MCTS(Game.state,Game.score)
            Game.step(di)
            state=copy.deepcopy(Game.state)
            score=Game.score
            a.cur_state(state,score)
            if(Game.gameover()):
                a.game_over(True)
                pygame.display.update()
                while(True):
                    for event in pygame.event.get():
                        if event.type==pygame.QUIT:
                            pygame.quit()
                            sys.exit(0)
            if Game.state.max()==2048:
                    while judge:
                      a.if_continue()
                      pygame.display.update()
                      for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit(0)
                        elif event.type==pygame.KEYDOWN:
                            if event.key==K_1:
                                judge=False
                                a.__init__()
                                a.cur_state(state,score)
                            if event.key==K_2:
                                a.__init__()
                                a.cur_state(state,score)
                                a.game_over(True)
                        pygame.display.update()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type==pygame.KEYDOWN:
                    if(event.key==K_e):
                        a.game_over(True)
                        pygame.display.update()
                        while True:
                            for event in pygame.event.get():
                                if event.type==pygame.QUIT:
                                    pygame.quit()
                                    sys.exit(0)
                        

                    
if __name__ == '__main__':
    main()        
    
    
    
    
    
    
    
    
    
    
       