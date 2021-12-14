# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

# @file agents.py
#
# @author Régis Clouard

import random
import copy
from math import sqrt
import utils
from dataclasses import dataclass

# Useful constants
EAT = 'eat'
DRINK = 'drink'
FORWARD = 'forward'
LEFT = 'left'
RIGHT = 'right'
WAIT = 'wait'

UNEXPLORED = -1
WALL = 0
SAND = 1
ROCK = 2
LETTUCE = 3
WATER = 4

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

DIRECTIONTABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)] # North, East, South, West

class TortoiseBrain:
    """
    The base class for various flavors of the tortoise brain.
    This an implementation of the Strategy design pattern.
    """
    def think( self, sensor ):
        raise Exception("Invalid Brain class, think() not implemented")

class RandomBrain( TortoiseBrain ):
    """
    An example of simple tortoise brain: acts randomly...
    """
    def init( self, grid_size ):
        pass

    def think( self, sensor ):
        return random.choice([EAT, DRINK, LEFT, RIGHT, FORWARD, FORWARD, WAIT])

class ReflexBrain( TortoiseBrain ):
    def init( self, grid_size ):
        pass

    def think( self, sensor ):
        # case 1: danger: dog
        if abs(sensor.dog_front) < 3 and abs(sensor.dog_right) < 3:
            if sensor.dog_front <= 0:
                if sensor.free_ahead:
                    return FORWARD
                elif sensor.dog_right > 0:
                    return LEFT
                else:
                    return RIGHT
            elif sensor.dog_front > 0:
                if sensor.dog_right > 0:
                    return LEFT
                else:
                    return RIGHT
        # increase the performance measure
        if sensor.lettuce_here and sensor.drink_level > 10: return EAT
        if sensor.water_ahead and sensor.drink_level < 50: return FORWARD
        if sensor.water_here and sensor.drink_level < 100: return DRINK
        # Nothing to do: move
        if sensor.free_ahead:
            return random.choice([FORWARD, RIGHT, FORWARD, WAIT, FORWARD, FORWARD, FORWARD])
        else:
            return random.choice([RIGHT, LEFT])
        return random.choice([EAT, DRINK, LEFT, RIGHT, FORWARD, FORWARD, WAIT])

 #  ______                               _              
 # |  ____|                             (_)             
 # | |__    __  __   ___   _ __    ___   _   ___    ___ 
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|



class GoalBasedBrain( TortoiseBrain ):
    grid = []
    positionDog = [-1,-1]
    grid_size = 0;
    caseToGo = (1,1)

    def updateAheadTile(self, sensor):
        direction=sensor.tortoise_direction
        x, y = sensor.tortoise_position

        x = x + DIRECTIONTABLE[direction][0]
        y = y + DIRECTIONTABLE[direction][1]
        if sensor.water_ahead:
            self.grid[y][x] = WATER
        elif sensor.lettuce_ahead :
            self.grid[y][x] = LETTUCE
        elif sensor.free_ahead :
            self.grid[y][x] = SAND
        else :
            if(self.grid[y][x] != WALL):
                self.grid[y][x] = ROCK
        
    def updateCurrentTitle(self, sensor):
        x, y = sensor.tortoise_position
       
        if sensor.water_here:
            self.grid[y][x] = WATER
        elif sensor.lettuce_here :
            self.grid[y][x] = LETTUCE
        else :
            self.grid[y][x] = SAND

    def distanceFromTheTurtle(self, sensor, title_x, title_y):
        x, y = sensor.tortoise_position
        distance = (abs(x-title_x))+(abs(y-title_y))
        return distance

    def nextUnexplored2(self, sensor):
        x,y = sensor.tortoise_position
        for i in range(4):
            next_x = x+DIRECTIONTABLE[i][0]
            next_y = y+DIRECTIONTABLE[i][1]
            if self.grid[next_y][next_x] == UNEXPLORED:
                self.caseToGo = (next_x, next_y)
                return next_x, next_y
        return None #Lancer algo recherche de chemin


    
    def nextUnexplored(self, sensor):
        unexplored_x=-1
        unexplored_y=-1
        distance=1e30
        x, y = sensor.tortoise_position
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j]==UNEXPLORED and self.distanceFromTheTurtle(sensor, i, j) < distance:
                    unexplored_x, unexplored_y = j,i
                    distance=self.distanceFromTheTurtle(sensor, i, j)
        if unexplored_x == -1:
            return None #no water title has been found, turtle must continue its exploration
        self.caseToGo = (unexplored_x, unexplored_y)
        return unexplored_x, unexplored_y


    def findClosestWater(self, sensor):
        water_x=-1
        water_y=-1
        distance=1e30
        x, y = sensor.tortoise_position
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j]==WATER and self.distanceFromTheTurtle(sensor, i, j) < distance:
                    water_x, water_y = i, j
                    distance=self.distanceFromTheTurtle(sensor, i, j)
        if water_x == -1:
            return None #no water title has been found, turtle must continue its exploration
        self.caseToGo = (water_x, water_y)
        return water_x, water_y

    
    def getActionDirection(self, sensor, x,y):
        currentX, currentY = sensor.tortoise_position   
        dx = currentX - x
        dy = currentY - y
        directionTortoise = sensor.tortoise_direction
        print("x :"+str(x)+" y :"+str(y),end="\n")
        print("currentX :"+str(currentX)+" currentY :"+str(currentY),end="\n")
        if(dx == 0):
            if(dy < 0):
                if(directionTortoise == SOUTH):
                    return FORWARD
                if(directionTortoise == EAST):
                    return RIGHT
                return LEFT
            else: 
                if(directionTortoise == NORTH):
                    return FORWARD
                if(directionTortoise == WEST):
                    return RIGHT
                return LEFT
        if(dy == 0):
            if(dx < 0):
                if(directionTortoise == EAST):
                    return FORWARD
                if(directionTortoise == SOUTH):
                    return LEFT
                return RIGHT
            else:
                if(directionTortoise == WEST):
                    return FORWARD
                if(directionTortoise == SOUTH):
                    return RIGHT
                return LEFT
        if(directionTortoise == SOUTH and dy < 0):
            return FORWARD
        if(directionTortoise == NORTH and dy > 0):
            return FORWARD
        if(dx < 0):
            if(directionTortoise == EAST):
                return FORWARD
            if(directionTortoise == SOUTH):
                return LEFT
            return RIGHT
        else:
            if(directionTortoise == WEST):
                return FORWARD
            if(directionTortoise == SOUTH):
                return RIGHT
            return LEFT

    def updateGridAfterEating(self, sensor, action):
        x, y = sensor.tortoise_position
        if(action == EAT):
            self.grid[x][y] = SAND
    

    def findBestActionToDo(self, sensor):
        
        if(sensor.lettuce_here):
            return EAT
        if(sensor.lettuce_ahead):
            return FORWARD
        if(sensor.drink_level < 50):
            x, y = sensor.tortoise_position
            if self.grid[x][y]==WATER:
                print("J'AI BU")
                return DRINK
            else:
                print("J'AI SOIF")
                co= self.findClosestWater(sensor) 
                if(co == None):
                    return WAIT
                return self.getActionDirection(sensor,co[0],co[1])
        else: 
            co = self.nextUnexplored(sensor)
            if(co == None):
                return WAIT
            return self.getActionDirection(sensor,co[0],co[1])


    def init( self, grid_size ):
        # *** YOUR CODE HERE ***"
        self.grid_size = grid_size
        for i in range(grid_size):
            tmp = []
            for j in range(grid_size):
                if(i == 0 or i == grid_size-1 or j == 0 or j == grid_size-1):
                    tmp.append(WALL)
                else :
                    tmp.append(UNEXPLORED)
            self.grid.append(tmp)
        
    def think( self, sensor ):
        """
        Returns the best action with regard to the current state of the game.
        Available actions are [EAT, DRINK, LEFT, RIGHT, FORWARD, WAIT].

        sensors attributes:
        sensor.free_ahead: there is no stone or wall one step ahead (boolean).
        sensor.lettuce_ahead: there is a lettuce plant one step ahead (boolean).
        sensor.lettuce_here: there is a lettuce plant at the current position (boolean).
        sensor.water_ahead: there is water one step ahead (boolean).
        sensor.water_here :there is water at the current position (boolean).
        sensor.drink_level : the level of water in the tortoise’s body, ranging from 100 to 0.
        sensor.health_level: the level of health in the tortoise’s body, ranging from 100 to 0.
        sensor.dog_front: the relative position of the dog, ie. the number of cells in front (positive) or behind (negative) the tortoise that it is.
        sensor.dog_right: the relative position of the dog to the right, ie. the number of cells to the right (positive) or left (negative) of the tortoise that it is.
        sensor.tortoise_position: the tortoise coordinates (x,y).
        sensor.tortoise_direction: the tortoise direction between 0 (north), 1 (east), 2 (south), and 3 (west).


        Compute the tortoise direction (dx,dy) in the grid from the sensor absolute direction.
        e.g: North -> (0, -1); South -> (0, 1)
        (dx, dy) = DIRECTIONTABLE[sensor.tortoise_direction]

        Compute the coordinates of the dog from the tortoise direction.
        if directionx == 0:
            self.dogx = self.x - directiony * sensor.dog_right
            self.dogy = self.y + directiony * sensor.dog_front
        else:
            self.dogx = self.x + directionx * sensor.dog_front
            self.dogy = self.y + directionx * sensor.dog_right
        """

        # *** YOUR CODE HERE ***"
        self.updateAheadTile(sensor)
        xTortoise, yTortoise = sensor.tortoise_position
        if(self.grid[yTortoise][xTortoise] == UNEXPLORED):
            self.updateCurrentTitle(sensor)
        if(self.caseToGo == sensor.tortoise_position or self.grid[self.caseToGo[1]][self.caseToGo[0]] == ROCK):
            print("Je suis ici")
            action = self.findBestActionToDo(sensor)
        else:
            action = self.getActionDirection(sensor, self.caseToGo[0],self.caseToGo[1])
        if(action == WAIT):
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    print(self.grid[i][j],end=" ")
                print("\n")
        self.updateGridAfterEating(sensor, action)
        # for i in range(self.grid_size):
        #     for j in range(self.grid_size):
        #         print(self.grid[i][j],end=" ")
            # print("\n")
        return action
