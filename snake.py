import math
import random
import pygame
import random
import tkinter as tk
from tkinter import messagebox

class cube():
    # rows is the number of rows in the grid
    rows = 20
    w = 500
    def __init__(self, start, dirnx=1, dirny=0, color=(255,0,0), isHead=False):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny # "L", "R", "U", "D"
        self.color = color
        self.isHead = isHead

    # change the position of the cube, depends on the give direction
    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos  = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)
            
    # draw the cube on the screen
    def draw(self, surface, eyes=False):
        # calculate the width of each cube
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]
        
        pygame.draw.rect(surface, self.color, (i*dis+1,j*dis+1,dis-2,dis-2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius,j*dis+8)
            circleMiddle2 = (i*dis + dis -radius*2, j*dis+8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)
        
    def setHead(self, isHead) : 
        self.isHead = isHead
        
    def isHead(self) : 
        return self.isHead

class snake():
    body = []
    turns = {}
    
    def __init__(self, color, pos):
        #pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
    
    def move(self, key) : 
        if isinstance(key, str) :
            if key == 'left' : 
                self.dirnx = -1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
            elif key == 'right' : 
                self.dirnx = 1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
            elif key == 'up' : 
                self.dirnx = 0
                self.dirny = -1
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
            elif key == 'down' :
                self.dirnx = 0
                self.dirny = 1
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        else : 
            # continue in same direction
            pass

        for i, c in enumerate(self.body):
            # creates a copy of the current position of the cube c.
            p = c.pos[:]
            # checks if the current position of the cube is in the turns dictionary.
            if p in self.turns:
                # retrieves the direction of the turn and updates the cube's position accordingly 
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                # if the current cube is the tail cube, remove the turn from the dictionary
                if i == len(self.body)-1:
                    self.turns.pop(p)
            else:
                # if the cube is not in the turns dictionary, move it in the current direction
                c.move(c.dirnx,c.dirny)
        
    def reset(self,pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    # add a cube to the snake
    # after eating a snack
    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny
        # check the direction of the tail cube and add the new cube in the correct position
        if dx == 1 and dy == 0:
            # if the tail is moving right, add the new cube to the left of the tail
            self.body.append(cube((tail.pos[0]-1,tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1,tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0],tail.pos[1]-1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0],tail.pos[1]+1)))
        # set the direction of the new cube to the direction of the tail
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy
    
    # draw the snake on the screen
    def draw(self, surface):
        for i,c in enumerate(self.body):
            # if it is the first cube, draw the eyes
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)
    
    # return example: (2, 17)*(3, 17)*(4, 17)*(5, 17)*(6, 17)*(7, 17)*(8, 17)*(9, 17)*(10, 17)
    def get_pos(self) : 
        positions = [p.pos for p in self.body]
        pos_str = "*".join([str(p) for p in positions])
        return pos_str
    

class SnakeGame:

    def __init__(self, rows) : 
        self.rows = rows
        self.players = {} 
        # used for mapping color of each snake to its id
        self.colorMap = {}
        self.snacks = [cube(randomSnack(rows)) for _ in range(5)] 
        print([s.pos for s in self.snacks])
    
    
    def add_player(self, user_id, color) : 
        # the key is the user_id, the value is the snake object
        self.players[user_id] = snake(color, (10,10))
        self.colorMap[user_id] = color
        print("adding player {} with color {}".format(user_id, color))
    
    def remove_player(self, user_id) :
        self.players.pop(user_id)
        self.colorMap.pop(user_id)
    
    def move(self, moves) :
        # generate a set of the ids of the players that moved
        # moves is a list of tuples (user_id, key)
        # For example, if moves is a list of tuples [(1, (1, 0)), (2, (0, 1)), (3, (-1, 0))],
        # the list comprehension [m[0] for m in moves] will return the list [1, 2, 3].
        moves_ids = set([m[0] for m in moves])
        # creates a set of player IDs that are not included in a set of move IDs
        still_ids = set(self.players.keys()) - moves_ids 
        # move the players that moved
        for move in moves : 
            self.move_player(move[0], move[1])
            print("moving player {} to {}".format(move[0], move[1]))

        # move the players that didn't move
        for still_id in still_ids :
            self.move_player(still_id, None)
            print("moving player {} in the same direction".format(still_id))
            
        for p_id in self.players.keys() :
            if self.check_collision(p_id) : 
                self.reset_player(p_id)

    def move_player(self, user_id, key = None) : 
        self.players[user_id].move(key)
    
    def reset_player(self, user_id) :
        x_start = random.randrange(1, self.rows-1)
        y_start = random.randrange(1, self.rows-1)
        self.players[user_id].reset((x_start, y_start))

    def get_player(self, user_id) : 
        return self.players[user_id].head.pos

    def check_collision(self, user_id) :
        for snack in self.snacks : 
            if self.players[user_id].head.pos == snack.pos : 
                self.snacks.remove(snack)
                self.snacks.append(cube(randomSnack(self.rows)))
                self.players[user_id].addCube()

        if self.players[user_id].head.pos in list(map(lambda z:z.pos,self.players[user_id].body[1:])):
            return True

        if self.players[user_id].head.pos[0] < 0 or self.players[user_id].head.pos[1] < 0 or self.players[user_id].head.pos[0] > self.rows-1 or self.players[user_id].head.pos[1] > self.rows-1:
            return True

        return False
    def get_state(self) : 
        """
        Returns a string representation of the current state of the game, 
        including the positions of all players and snacks.
        
        Returns:
        str: A string representation of the current state of the game.
        """
        players_pos = [p.get_pos() for p in self.players.values()]
        players_pos_str = "**".join(players_pos)
        snacks_pos = "**".join([str(s.pos) for s in self.snacks])
        return players_pos_str + "|" + snacks_pos


# generate a random snack, row is the number of rows in the grid
def randomSnack(rows):
    x = random.randrange(1,rows-1)
    y = random.randrange(1,rows-1)
    return (x,y)



    
if __name__ == "__main__":
    pass