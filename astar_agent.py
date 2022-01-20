import time
import random
from copy import deepcopy

from numpy import empty
from agent import Agent


#  use whichever data structure you like, or create a custom one
import queue
import heapq
from collections import deque


"""
  you may use the following Node class
  modify it if needed, or create your own
"""
class Node():
    
    def __init__(self, parent_node, player_pos, g, h_value, f_value): 
        self.parent_node = parent_node
        self.player_pos = player_pos
        self.g = g
        self.h = h_value
        self.f = f_value



class PriorityQueue: 
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]


class AStarAgent(Agent):

    def __init__(self):
        super().__init__()
        
        #  g cost in A*
        #    IMPORTANT NOTE!!!
        #please fill values inside this array
        #as you perform the A* search!
        self.g_values = []
        
        
        #  a large enough value for initializing g values at the start
        self.INFINITY_COST = 2**10


        self.direction = [[-1,0],[1,0],[0,1],[0,-1]]    #UP, DOWN, RIGHT, LEFT 
        
        
    
    #  finds apple's position in the given level matrix
    #return a tuple of (row, column)
    def find_apple_position(self, level_matrix):
        for r in range(len(level_matrix)):
            for c in range(len(level_matrix[0])):
                if (level_matrix[r][c] == "A"):
                    return (r, c)
        
        return (-1, -1)
        
    
    #  calculates manhattan distance between player and apple
    #this function assumes there is only a single apple in the level
    def heuristic(self, player_row, player_column, apple_row, apple_column):
        return abs(player_row - apple_row) + abs(player_column - apple_column)
    
    ###--- Function for generating a key value for sorting ---###
    def get_f_Value(self,Node):
        return Node.f

    ###--- Function for generating a key value for sorting ---###
    def get_fh_Value(self,Node):
        return Node.f, Node.h

    ###--- Function for generating a key value for sorting ---###
    def get_fhg_Value(self,Node):
        return Node.f, Node.h, Node.g
    
    ###--- Function for generating a move sequence ---###
    def get_road(self,Node, player_pos):
        pos = Node.player_pos
        g = self.g_values[pos[0]][pos[1]]
        road = []
        
        while pos != player_pos:
            for i in self.direction:
                if g > self.g_values[pos[0] + i[0]][pos[1] + i[1]]:
                    if i == [0,-1]:
                        road.insert(0,"R")
                    elif i == [0,1]:
                        road.insert(0,"L")
                    elif i == [-1,0]:
                        road.insert(0,"D")
                    elif i==[1,0]:
                        road.insert(0,"U")
                    g = self.g_values[pos[0] + i[0]][pos[1] + i[1]]
                    pos = [pos[0] + i[0],pos[1] + i[1]]
                    break
        return road

    def solve(self, level_matrix, player_row, player_column):
        super().solve(level_matrix, player_row, player_column)
        move_sequence = []

       

        initial_level_matrix = [list(row) for row in level_matrix] #deepcopy(level_matrix)
        
        
        level_height = len(initial_level_matrix)
        level_width = len(initial_level_matrix[0])
        
       
        #  initialize g values
        self.g_values = [ [self.INFINITY_COST]*level_width for i in range(level_height) ]
        
        #  initialize g of starting position 0
        self.g_values[player_row][player_column] = 0
        
        #  calculate heuristic value for starting position
        (apple_row, apple_column) = self.find_apple_position(initial_level_matrix)
        initial_heuristic = self.heuristic(player_row, player_column, apple_row, apple_column)
        
        print("A* solve() --- level size:", (level_height, level_width))
        print("A* solve() --- apple position:", (apple_row, apple_column))
        print("A* solve() --- initial_heuristic:", initial_heuristic)
        
        
        
        """
            YOUR CODE STARTS HERE
            fill move_sequence list with directions chars
        """
        ###--- Initializing necessary lists and booleans ---###
        queue = []   
        visited = []
        nodes_in_queue = []
        finished = False
        
        player_pos = [self.player_row,self.player_col]
        
        ###--- Creating first node ---###
        first_node = Node(None, player_pos, self.g_values[player_pos[0]][player_pos[1]], initial_heuristic, initial_heuristic)
        queue.append(first_node)

        while queue and not finished:

            ###--- Tie Breaking Options ---###
            # queue.sort(key = self.get_f_Value)          #Tie breaking by choosing what is on top of queue
            # queue.sort(key = self.get_fh_Value)       #Tie breaking by smallest h values if there is a tie break in f values
            queue.sort(key = self.get_fhg_Value)      #Tie breaking by smallest g values after tie breaking by smallest h if there is still a tie break 
            ###################################

            ###--- Choosing next node ---###
            head_node = queue.pop(0)
            self.expanded_node_count += 1
            current_pos = head_node.player_pos

            ###--- Exploring Up,Down,Right and Left nodes ---###
            for i in self.direction:
                next_pos = [current_pos[0] + i[0],current_pos[1] + i[1]]
                ###--- Looking for walls if there is any ---###
                if level_matrix[next_pos[0]][next_pos[1]] != "W":
                    ###--- Answer to: Will next move find the apple? ---### 
                    if (next_pos[0] == apple_row) and (next_pos[1] == apple_column):
                        ###--- Calculating g,h and f values ---###
                        g_new = self.g_values[current_pos[0]][current_pos[1]] + 1
                        ###--- Update g_value if there is a shorter way ---###
                        if self.g_values[next_pos[0]][next_pos[1]] > g_new:
                            self.g_values[next_pos[0]][next_pos[1]] = g_new
                        h_new = self.heuristic(next_pos[0], next_pos[1], apple_row, apple_column)
                        f_new = g_new + h_new
                        
                        ###--- Creating last node (Apple is on this node) ---###
                        last_node = Node(head_node, next_pos, g_new, h_new, f_new)
                        self.generated_node_count += 1
                        finished = True
                    ###--- If next node not visited ---###
                    elif next_pos not in visited:
                        ###--- Calculating g,h and f values ---###
                        g_new = self.g_values[current_pos[0]][current_pos[1]] + 1
                        ###--- Update g_value if there is a shorter way ---###
                        if self.g_values[next_pos[0]][next_pos[1]] > g_new:
                            self.g_values[next_pos[0]][next_pos[1]] = g_new
                        h_new = self.heuristic(next_pos[0], next_pos[1], apple_row, apple_column)
                        f_new = g_new + h_new
                        ###--- If node is not already in queue ---###
                        if next_pos not in nodes_in_queue:
                            new_node = Node(head_node, next_pos, g_new, h_new, f_new)
                            queue.append(new_node)
                            nodes_in_queue.append(next_pos)
                            self.generated_node_count += 1
            ###--- Append node as visiited ---###
            visited.append(current_pos)

            if (len(queue) > self.maximum_node_in_memory_count):
                self.maximum_node_in_memory_count = len(queue)
                        
        ###--- Generating moving sequence ---###
        move_sequence = self.get_road(last_node, player_pos)
        """
            YOUR CODE ENDS HERE
            return move_sequence
        """
        return move_sequence
