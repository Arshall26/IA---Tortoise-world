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
import time
from utils import PriorityQueue

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
LETTUCE = 2
WATER = 3

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
    pathToFollow = []
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
            self.grid[y][x] = WALL
                
        
        
    def updateCurrentTitle(self, sensor):
        x, y = sensor.tortoise_position
       
        if sensor.water_here:
            self.grid[y][x] = WATER
        elif sensor.lettuce_here :
            self.grid[y][x] = LETTUCE
        else :
            self.grid[y][x] = SAND

    def updateGridAfterEating(self, sensor):
        x, y = sensor.tortoise_position
        self.grid[y][x] = SAND

    def getSuccessorsSquare(self, square, direction):
        successors = []
        x,y = square
        if(self.grid[y + DIRECTIONTABLE[direction][1]][x + DIRECTIONTABLE[direction][0]] != WALL ):
            successors.append(( (x + DIRECTIONTABLE[direction][0], y + DIRECTIONTABLE[direction][1]), direction, FORWARD, 2))
        successors.append(((x,y), (direction - 1) % 4, LEFT, 1))
        successors.append(((x,y), (direction + 1) % 4, RIGHT, 1))
        return successors

    def findPath(self, sensor, goalSquare):
        open_list = PriorityQueue()
        open_list.push([(sensor.tortoise_position, sensor.tortoise_direction, None)], 0)
        closed_list = set([(sensor.tortoise_position, sensor.tortoise_direction)])

        while not open_list.isEmpty():
            current_path, cost = open_list.pop()
            current_square, current_direction, current_action = current_path[-1]

            if self.grid[current_square[1]][current_square[0]] == goalSquare:
                
                return (list (map(lambda x : x[2], current_path[1:])))
            else:
                next_steps = self.getSuccessorsSquare(current_square, current_direction)
                for case, direction, action, weigth in next_steps:
                    if (case,direction) not in closed_list:
                        closed_list.add((case,direction))
                        open_list.push((current_path + [(case,direction,action)]), cost+weigth)
        return []

    def init( self, grid_size ):
        # *** YOUR CODE HERE ***"
        self.grid = []
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

        #Update the tile underneath and ahead of the turtoise
        xTortoise, yTortoise = sensor.tortoise_position
        if(self.grid[yTortoise][xTortoise] == UNEXPLORED):
            self.updateCurrentTitle(sensor)
        self.updateAheadTile(sensor)

        if(sensor.lettuce_here): # Of course, the tortoise has to eat the lettuce.
            self.updateGridAfterEating(sensor)
            return EAT
        if(sensor.lettuce_ahead): #A lettuce has been found, we have to eat it.
            self.pathToFollow = [] # We suppress the path that we had to follow
            return FORWARD # It will be eaten during the next turn.
        if(sensor.water_here and sensor.drink_level < 90): # Drink only if necesseray.
            return DRINK
        if(sensor.drink_level < 50): # Find the closest water source of the turtoise.
            pathToWater = self.findPath(sensor, WATER)
            if(pathToWater != []): # Only if a water has been found, we change our path.
                self.pathToFollow = pathToWater
        
        #If we have no path to follow, we have to recalculate a new one.
        if(self.pathToFollow == []):
            self.pathToFollow = self.findPath(sensor, UNEXPLORED)
        # If at anytime the turtoise is block by a wall or a rock, we have to change our path.
        if(not sensor.free_ahead and self.pathToFollow[0] == FORWARD):
            self.pathToFollow = self.findPath(sensor, UNEXPLORED)

        action = self.pathToFollow.pop(0)
        # for i in range(self.grid_size):
        #     for j in range(self.grid_size):
        #         print(self.grid[i][j],end=" ")
        #     print("\n")
        return action
