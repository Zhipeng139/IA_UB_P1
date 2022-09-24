#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""
from itertools import permutations
import copy

import chess
import numpy as np
import sys
import queue
from typing import List
from collections import defaultdict

RawStateType = List[List[List[int]]]


class Aichess():
    """
    A class to represent the game of chess.

    ...

    Attributes:
    -----------
    chess : Chess
        represents the chess game

    Methods:
    --------
    startGame(pos:stup) -> None
        Promotes a pawn that has reached the other side to another, or the same, piece

    """

    def __init__(self, TA, myinit=True):

        if myinit:
            self.chess = chess.Chess(TA, True)
        else:
            self.chess = chess.Chess([], False)

        self.listNextStates = []
        self.listVisitedStates = []
        self.pathToTarget = []
        self.currentStateW = self.chess.boardSim.currentStateW
        self.depthMax = 8
        self.checkMate = False

    def getCurrentState(self):

        return self.myCurrentStateW

    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def isSameState(self, a, b):

        isSameState1 = True
        # a and b are lists
        for k in range(len(a)):

            if a[k] not in b:
                isSameState1 = False

        isSameState2 = True
        # a and b are lists
        for k in range(len(b)):

            if b[k] not in a:
                isSameState2 = False

        isSameState = isSameState1 and isSameState2
        return isSameState

    def isVisited(self, mystate):

        if (len(self.listVisitedStates) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedStates)):

                    if self.isSameState(list(perm_state[j]), self.listVisitedStates[k]):
                        isVisited = True

            return isVisited
        else:
            return False

    def do_movement(self, standard_current_state, standard_next_state):
        start = [e for e in standard_current_state if e not in standard_next_state]
        to = [e for e in standard_next_state if e not in standard_current_state]
        start, to = start[0][0:2], to[0][0:2]
        self.chess.moveSim(start, to)

    def isCheckMate(self, mystate):

        # Your Code
        checkMateState = [
            {(0,0,2),(2,4,6)},
            {(0,1,2),(2,4,6)},
            {(0,2,2),(2,4,6)},
            {(0,3,2),(2,4,6)},
            {(0,5,2),(2,4,6)},
            {(0,6,2),(2,4,6)},
            {(0,7,2),(2,4,6)}
        ]

        self.checkMate = (mystate in checkMateState)

    def to_set(self, state):
        set_of_states = set()

        for piece in state:
            tup = tuple(piece)
            set_of_states.add(tup)
        return set_of_states        
    def to_list(self, state):
        return [list(e) for e in state]

    def DepthFirstSearch(self, currentState, depth):
        
        path = []
        self.listVisitedStates.append(self.to_set(currentState))
        # Your Code here
        def backtraking(currentState, depth):
            if self.checkMate:
                return True
            if depth == self.depthMax:
                return False

            list_of_states = self.getListNextStatesW(currentState)

            for state in list_of_states:
                set_state = self.to_set(state)

                if set_state not in self.listVisitedStates:
                    self.listVisitedStates.append(set_state)
                    self.isCheckMate(set_state)
                    path.append(state)
                    self.do_movement(currentState, state)
                    if backtraking(state, depth+1):
                        self.pathToTarget = path
                        return True
                    self.do_movement(state, currentState)
                    path.pop()          
           
        backtraking(currentState, depth)

    def getPath (self, parent, start):
        result = []
        node = start

        while node != None:
            result.append(node)
            prev = parent[frozenset(self.to_set(node))]
            node = prev
        result.pop()
        result.reverse()
        return result
    def BreadthFirstSearch(self, currentState, depth=0):
        # Your Code here

        #Queue need to store the current state, depth and copyed Aichess class
        q = queue.Queue()
        #Store prev State
        parent = defaultdict()

        q.put((currentState, depth, copy.deepcopy(self)))

        init_set_state = self.to_set(currentState)
        self.listVisitedStates.append(init_set_state)
        parent[frozenset(init_set_state)] = None

        while q:
            current_state, current_depth, current_aichess = q.get()

            if current_depth <= self.depthMax:
                list_of_states = current_aichess.getListNextStatesW(current_state)

                for state in list_of_states:
                    set_state = self.to_set(state)
                    if set_state not in self.listVisitedStates:
                        self.listVisitedStates.append(set_state)
                        parent[frozenset(set_state)] = current_state
                        self.isCheckMate(set_state)
                        if self.checkMate:
                            print('Check Mate')
                            print('path=>', self.getPath(parent, state))
                            return
                        list_set_state = self.to_list(set_state)
                        copy_aichess = copy.deepcopy(current_aichess)
                        copy_aichess.do_movement(current_state, list_set_state)
                        q.put((list_set_state,current_depth+1, copy_aichess))

                    





    def AStarSearch(self, currentState):

        # Your Code here
        return


def translate(s):
    """
    Translates traditional board coordinates of chess into list indices
    """

    try:
        row = int(s[0])
        col = s[1]
        if row < 1 or row > 8:
            print(s[0] + "is not in the range from 1 - 8")
            return None
        if col < 'a' or col > 'h':
            print(s[1] + "is not in the range from a - h")
            return None
        dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return (8 - row, dict[col])
    except:
        print(s + "is not in the format '[number][letter]'")
        return None


if __name__ == "__main__":
    #   if len(sys.argv) < 2:
    #       sys.exit(usage())

    # intiialize board
    TA = np.zeros((8, 8))
    # white pieces
    # TA[0][0] = 2
    # TA[2][4] = 6
    # # black pieces
    # TA[0][4] = 12

    TA[7][0] = 2
    TA[7][4] = 6
    TA[0][4] = 12

    #TA[0][0] = 2
    #TA[1][0] = 6
    #TA[0][1] = 12

    # initialise board
    print("stating AI chess... ")
    aichess = Aichess(TA, True)
    currentState = aichess.chess.board.currentStateW.copy()

    print("printing board")
    aichess.chess.boardSim.print_board()

    # get list of next states for current state
    print("current State", currentState)

    # it uses board to get them... careful
    aichess.getListNextStatesW(currentState)
    #   aichess.getListNextStatesW([[7,4,2],[7,4,6]])
    print("list next states ", aichess.listNextStates)

    # starting from current state find the end state (check mate) - recursive function
    # aichess.chess.boardSim.listVisitedStates = []
    # find the shortest path, initial depth 0
    depth = 0
    aichess.BreadthFirstSearch(currentState)
    #aichess.DepthFirstSearch(currentState, depth)

    # MovesToMake = ['1e','2e','2e','3e','3e','4d','4d','3c']

    # for k in range(int(len(MovesToMake)/2)):

    #     print("k: ",k)

    #     print("start: ",MovesToMake[2*k])
    #     print("to: ",MovesToMake[2*k+1])

    #     start = translate(MovesToMake[2*k])
    #     to = translate(MovesToMake[2*k+1])

    #     print("start: ",start)
    #     print("to: ",to)

    #     aichess.chess.moveSim(start, to)

    # aichess.chess.boardSim.print_board()
    print("#Move sequence...  ", aichess.pathToTarget)
    print("#Visited sequence...  ", aichess.listVisitedStates)
    print("#Current State...  ", aichess.chess.board.currentStateW)
