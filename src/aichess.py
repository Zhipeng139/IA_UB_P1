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

import timeit

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
        return self.CurrentStateW

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
        '''

        Args:
            standard_current_state: current state of board
            standard_next_state: next state of board

        Returns: the movement of pieces

        '''
        start = [e for e in standard_current_state if e not in standard_next_state]
        to = [e for e in standard_next_state if e not in standard_current_state]
        start, to = start[0][0:2], to[0][0:2]
        self.chess.moveSim(start, to)

    def isCheckMate(self, mystate):
        '''

        Args:
            mystate: current state

        Returns: if the state is checkmate

        '''
        # Your Code
        checkMateState = [
            {(0,0,2),(2,4,6)},
            {(0,1,2),(2,4,6)},
            {(0,2,2),(2,4,6)},
            {(0,6,2),(2,4,6)},
            {(0,7,2),(2,4,6)}
        ]

        self.checkMate = (mystate in checkMateState)

    def to_set(self, state):
        '''

        Args:
            state: state which want to change to a set

        Returns: a state with set type

        '''
        set_of_state = set()

        for piece in state:
            tup = tuple(piece)
            set_of_state.add(tup)
        return set_of_state

    def DepthFirstSearch(self, currentState, depth):

        # list to store the final path
        path = []
        self.listVisitedStates.append(self.to_set(currentState))
        def backtraking(currentState, depth):

            # verify if is the end case
            if self.checkMate:
                return True
            if depth == self.depthMax:
                return False

            list_of_states = self.getListNextStatesW(currentState)

            # expanded the list of next states
            for state in list_of_states:
                set_state = self.to_set(state)

                # do movement and add the state to path if the state is not visited
                if set_state not in self.listVisitedStates:
                    self.listVisitedStates.append(set_state)
                    self.isCheckMate(set_state)
                    path.append(state)
                    self.do_movement(currentState, state)
                    if backtraking(state, depth+1):
                        self.pathToTarget = path
                        return True

                    # if the movement is wrong, do backtracking and cancel the movement
                    self.do_movement(state, currentState)
                    path.pop()          
           
        backtraking(currentState, depth)

    def getPath (self, parent, start):
        '''

        Args:
            parent: diccionary which recorded the parent state of current state
            start: the first state

        Returns: a list of states

        '''

        # list to store the result path
        result = []
        node = start

        while node != None:
            result.append(node)
            prev = parent[frozenset(self.to_set(node))]
            node = prev
        result.pop()
        result.reverse()
        return result

    def BreadthFirstSearch(self, currentState):
        '''

        Args:
            currentState: start board State

        '''

        #Queue need to store the current state, depth and copyed Aichess class
        q = queue.Queue()

        # dictionary to store the previous state
        parent = defaultdict()

        q.put((currentState, 0, copy.deepcopy(self)))

        init_set_state = self.to_set(currentState)
        self.listVisitedStates.append(init_set_state)

        parent[frozenset(init_set_state)] = None

        while q:
            # get first element of queue
            current_state, current_depth, current_aichess = q.get()

            if current_depth <= self.depthMax:
                list_of_states = current_aichess.getListNextStatesW(current_state)

                # expanded the next states
                for state in list_of_states:
                    set_state = self.to_set(state)

                    # do movement if the state is not visited
                    if set_state not in self.listVisitedStates:
                        self.listVisitedStates.append(set_state)
                        parent[frozenset(set_state)] = current_state
                        self.isCheckMate(set_state)
                        if self.checkMate:
                            self.pathToTarget = self.getPath(parent, state)
                            for state in self.pathToTarget:                                
                                self.do_movement(currentState, state)
                                currentState = state
                            return
                        copy_aichess = copy.deepcopy(current_aichess)
                        copy_aichess.do_movement(current_state, state)
                        q.put((state,current_depth+1, copy_aichess))
        



    def calculate_dis(self, state):
        black_king = self.chess.boardSim.currentStateB[0]

        x1, y1 = black_king[0:2]
        x2, y2 = state[0:2]

        piece_type = state[2]

        #If the piece is a Rook using manhattan distance
        if piece_type == 2:
            return abs(x1 - x2)+abs(y1 - y2)
        #If the piece is a King using chebyshev distance
        elif piece_type == 6:
            return max(abs(x1 - x2), abs(y1 - y2))
        
    def all_distance(self, states): # return the all of distances of 2 pieces
        for state in states:
            yield self.calculate_dis(state)

    def AStarSearch(self, currentState, depth = 0):

        #Store the current distance, current state, depth and copyed Aichess class using a priority queue
        q = queue.PriorityQueue()
        q.put((sum(self.all_distance(currentState)), currentState, depth ,copy.deepcopy(self)))

        # dictionary to store the previous state
        parent = defaultdict()

        init_set_state = self.to_set(currentState)
        self.listVisitedStates.append(init_set_state)

        parent[frozenset(init_set_state)] = None

        while q:

            # get first element of queue
            current_dist, current_state, current_depth, current_aichess = q.get()

            if current_depth <= self.depthMax:
                list_of_states = current_aichess.getListNextStatesW(current_state)

                # expanded the next states
                for state in list_of_states:
                    set_state = self.to_set(state)

                    # do movement if the state is not visited
                    if set_state not in self.listVisitedStates:
                        self.listVisitedStates.append(set_state)
                        parent[frozenset(set_state)] = current_state
                        self.isCheckMate(set_state)
                        if self.checkMate:
                            self.pathToTarget = self.getPath(parent, state)
                            for state in self.pathToTarget:                                
                                self.do_movement(currentState, state)
                                currentState = state
                            return
                        copy_aichess = copy.deepcopy(current_aichess)
                        copy_aichess.do_movement(current_state, state)
                        q.put((max(self.all_distance(state))+current_depth, state, current_depth+1, copy_aichess))

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

    TA = np.zeros((8, 8))

    TA[7][0] = 2
    TA[7][4] = 6
    TA[0][4] = 12

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

    depth = 0    
    #aichess.BreadthFirstSearch(currentState)
    aichess.DepthFirstSearch(currentState, depth)
    #aichess.AStarSearch(currentState)

    print("#Move sequence...  ", aichess.pathToTarget)
    print("#Visited sequence...  ", aichess.listVisitedStates)
    print("#Current State...  ", aichess.chess.board.currentStateW)
    print("#Final Board")
    aichess.chess.boardSim.print_board()
