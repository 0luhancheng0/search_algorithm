import argparse as ap
import re
import platform

######## RUNNING THE CODE ####################################################
#   You can run this code from terminal by executing the following command
#   python planpath.py <INPUT/input#.txt> <OUTPUT/output#.txt> <flag> <algorithm>
#   for example: python planpath.py INPUT/input2.txt OUTPUT/output2.txt 0 A
#   NOTE: THIS IS JUST ONE EXAMPLE INPUT DATA
###############################################################################


################## YOUR CODE GOES HERE ########################################
import math


class Action:
    """
    An action represent the operator
    """
    def __init__(self, action):
        """
        class that represent action 
        the move is a vector represent the direcotion of movement
        """
        self.action_str = action
        self.move = [0, 0]
        if 'R' in action:
            self.move[1] += 1
        if 'L' in action:
            self.move[1] -= 1
        if 'U' in action:
            self.move[0] -= 1
        if 'D' in action:
            self.move[0] += 1
        if len(action) == 1:
            self.cost = 2
        else:
            self.cost = 1
    def get_cost(self):
        return self.cost
    def from_coord(self, coord):
        """get new coordinate from old coordinate with current action
        
        Arguments:
            coord {Coordinate} -- A coordinate type
        
        Returns:
            Coordinate -- where it will land by take action from old coordinate
        """
        return coord.take_action(self)
    def __repr__(self):
        return self.action_str

class Coordinate:
    """
    Coordinate represent the coordinate of each tile as (x, y)
    start from top left 
    """
    def __init__(self, x, y):
        self.x = x 
        self.y = y 
    def __repr__(self):
        return '({0}, {1})'.format(self.x, self.y)
    def take_action(self, action):
        return Coordinate(self.x + action.move[0], self.y + action.move[1])
        

import numpy as np
class Map:
    """
    Map object represent input map
    """
    def __init__(self, fname):
        self.M = []
        with open(fname, 'r') as f:
            self.size = int(f.readline().rstrip())
            for i in f:
                self.M.append(list(i.rstrip()))
        self.M = np.array(self.M)

        # ensure there is one and only one start/goal node in map
        if (self.M == 'S').sum() != 1:
            raise Exception('there need to be one and only one start position')
        if (self.M == 'G').sum() !=1:
            raise Exception('there need to be one and only one goad position')
    def __contains__(self, coord):
        """test if coordinate is in the map
        
        Arguments:
            coord {Coordinate} -- the location 
        
        Returns:
            boolean -- in the map or not
        """
        return  0 <= coord.x < self.size and 0 <= coord.y < self.size
    def __repr__(self):
        """repr of map
        
        Returns:
            string -- a string thats going to be printed out
        """
        output_str = '\n'
        for i in self.M:
            output_str += ''.join(i)
            output_str += '\n'
        # output_str = [for i in self.M]
        # output_str = output_str[:-1]
        return output_str
    def get_normal_num(self):
        """get the total number of normal tile in map
        
        Returns:
            int -- number of normal tile
        """
        return np.sum(self.M == 'R')
    def get_size(self):
        """get the size of map
        
        Returns:
            int -- size of map
        """
        return self.size
    def get_map(self):
        return self.M
    def get_tile_coord(self, tile):
        """get the coordinate for a type of tile, return after first occurence found
        
        Arguments:
            tile {string} -- which type of file you want
        
        Returns:
            Coordinate -- the location of such tile
        """
        # for i in range(len(self.M)):
        #     for j in range(len(self.M[i])):
        #         if self.M[i][j] == tile:
        #             return Coordinate(i, j)
        idx = np.nonzero(self.M == tile)
        target = self.M[idx]
        # print(self.M[idx])
        if len(target) == 0:
            raise Exception('Tile type {} not found in map'.format(tile))
        elif len(target) > 1:
            raise Exception('Multiple tile type {} found in map'.format(tile))
        else:
            # print(result)
            # return Coordinate(result[0], result[1])
            return Coordinate(idx[0][0], idx[1][0])
    def get_coord_tile(self, coord):
        """get the tile of some coordinate
        
        Arguments:
            coord {Coordinate} -- a location on the map
        
        Returns:
            string -- the type of tile on that location
        """
        return self.M[coord.x, coord.y]
    def get_goal_coord(self):
        """get the coordinate of goal
        
        Returns:
            Coordinate -- the location of goal
        """
        return self.get_tile_coord('G')
    def get_start_coord(self):
        """get the coordinate of start 
        
        Returns:
            Coordinate -- the location of start
        """
        return self.get_tile_coord('S')
    def can_move(self, coord, action):
        """test if agent can take given action from given coordinate
        
        Arguments:
            coord {Coordinate} -- the location on map
            action {Action} -- an action to take
        
        Returns:
            boolean -- the such action can be taken
        """

        # decompose action to two seperate action, and test them individually can_move(RD) -> can_move(R) and can_move(D)
        if len(action.action_str) == 2:
            if not (self.can_move(coord, Action(action.action_str[0])) and self.can_move(coord, Action(action.action_str[1]))):
                return False
        destination_coord = action.from_coord(coord)

        # test if destination land out of map or on mountain
        return (destination_coord in self) and (self.get_coord_tile(destination_coord) != 'X')

# the order of Actions in ALL_ACTIONS is also the tie breaking order for DLS
ALL_ACTIONS = [Action(i) for i in ['R', 'RD', 'D', 'LD', 'L', 'LU', 'U', 'RU']]
ALL_TILE_TYPES = ['R', 'X', 'S', 'G']




class Node:
    def __init__(self, seq, operator, parent, input_map, node_depth, procedure_name, expansion_order):
        self.expansion_order = expansion_order
        self.seq = seq
        self.operator = operator
        if seq != 0:
            self.coord = operator.from_coord(parent.coord)
            self.g = operator.get_cost() + parent.g
        else:
            self.coord = input_map.get_start_coord()
            self.g = 0
        self.node_depth = node_depth
        if procedure_name == 'A':
            self.h = heuristic_func(self.coord, input_map, procedure_name)
        else:
            self.h = 0
            self.g = 0
        self.f = self.h + self.g
        self.tile = input_map.get_coord_tile(self.coord)
        self.children = []
        self.parent = parent
        self.input_map = input_map
    def __eq__(self, value):
        return self.coord.x == value.coord.x and self.coord.y == value.coord.y 
    def is_goal(self):
        """test if current node is goal"""
        return self.tile == 'G'
    def get_identifier(self):
        return 'N'+str(self.seq)
    
    def get_availble_operators(self):
        """get all action current node can take
        
        Returns:
            [Action] -- a list of action which can be taken by current node 
        """
        result = []
        for i in ALL_ACTIONS:
            if self.input_map.can_move(self.coord, i):
                result.append(i)
        return result

    def expand(self, close_list, seq_counter, procedure_name, expansion_order):
        """expand current node
        
        Arguments:
            procedure {string} -- which algorithm to use
            close_list {ClosedList} -- the closed list, will not be used if procedure is D
            seq_counter {int} -- the sequence number for expansion, which will be used in assign id for children
        
        Returns:
            [node], int -- a list of children node, and incremented sequence counter
        """
        all_available_operators = self.get_availble_operators()
        for i in all_available_operators:
            next_coord = i.from_coord(self.coord)
            if next_coord in close_list:
                continue
            generated_node = Node(
                seq_counter, i, self, self.input_map, self.node_depth+1,procedure_name, None)
            self.children.append(generated_node)
            seq_counter += 1
        self.expansion_order = expansion_order
        return self.children, seq_counter
    def get_path(self):
        """get the path to node
        
        Returns:
            string -- the string sequence consist of operators which could be used for generating current node from start
        """
        current = self
        solution = ''
        while current.operator is not None:
            solution = '-' + current.operator.action_str + solution
            current = current.parent
        solution = 'S' + solution
        return solution





def contains(lst, coord):
    """test if coord is contained by list
    Arguments:
        lst {list} -- the internal implementation of either closed or open list
        coord {Coordinate} -- the position on map
    
    Returns:
        (bool, index) -- first return value represent if coord is contained by lst, if True, then index will be returned in second element, otherwise return (False, None)
    """
    for i in range(len(lst)):
        if coord.x == lst[i].coord.x and coord.y == lst[i].coord.y:
            return True, i
    return False, None

class CloseList:
    """
    Closed list 
    Used in graph search, maintain a list of visited node
    """
    def __init__(self):
        self.lst = []
    def __contains__(self, coord):
        """test if a coordinate has been visited
        
        Arguments:
            coord {Coordinate} -- the location on ma
        
        Returns:
            bool -- if input coordinate has been visited
        """
        result, _ = contains(self.lst, coord)
        return result
    def add(self, element):
        self.lst.append(element)
    def __repr__(self):
        output_str = 'CLOSED' + ":\t{"
        for node in self.lst:
            output_str += "(N{seq}: expansion_order={expansion_order} g={g} h={h:.2f} f={f:.2f}), ".format(**
                                                                            vars(node), path=node.get_path())
        output_str = output_str[:-2]
        output_str += '}'
        return output_str

class OpenList:
    """
    frontier, maintain a list of nodes generated and yet to be expanded
    """
    def __init__(self, procedure):
        self.procedure = procedure
        self.lst = []
    def __contains__(self, coord):
        result, _ = contains(self.lst, coord)
        return result
    def pop(self):
        """get next node to be expanded and remove the node from list
        if DLS is chosen, then return the first element in the list
        if A is chosen, then select the node with lowest f value
        
        Keyword Arguments:
            _ {self} -- [description] (default: {contains(self.lst, coord)returnresultdefpop(self})
        
        Returns:
            [Node] -- [the next node to be expanded]
        """
        if self.procedure == 'A':
            current_target = 0
            for i in range(len(self.lst)):
                if self.lst[i].f < self.lst[current_target].f:
                    current_target = i
            result = self.lst.pop(current_target)
            return result
        else:
            return self.lst.pop(0)
    def add_children(self, children, close_list):
        """add children node to open list 
        
        Arguments:
            children {[Node]} -- a list node to be added
            close_list {ClosedList} -- the closed list, if a node already in closed list, it will not be added to current list. The closed list for DLS is empty.
        """
        # prepend the children to close_list if procedure is D
        if self.procedure == 'D':
            temp = children.copy()
            temp.extend(self.lst)
            self.lst = temp
        else:
            for i in children:

                # check if child node is already in closed list
                if i.coord in close_list:
                    continue
                else:
                    if i.coord in self:

                        # check if child node is already in open list
                        _, idx = contains(self.lst, i.coord)

                        # check if g update is needed
                        if self.lst[idx].g > i.g:
                            self.lst[idx].g = i.g 
                            self.lst[idx].parent = i.parent
                        else:
                            continue
                    else:
                        self.lst.append(i)
                    

    def __repr__(self):
        output_str = "OPEN" + ":\t{"
        for node in self.lst:
            output_str += "(N{seq}: {path} g={g} h={h:.2f} f={f:.2f}), ".format(**
                                                                            vars(node), path=node.get_path())
        output_str = output_str[:-2]
        output_str += '}'
        return output_str
    def __len__(self):
        return len(self.lst)

def heuristic_func(current_coord, input_map, procedure):
    """heuristic function for A
    it will take problem and state as input and output a value which represent how far 
    away the state is from reaching the goal, such estimation is implemented with relaxed version of problem
    
    Arguments:
        current_coord {Coordinate} -- the coordinate represent the current location on map
        input_map {Map} -- represent the problem
        procedure {string} -- either D or A
    
    Returns:
        int -- the heuristic value
    """
    goal_coord = input_map.get_goal_coord()
    if procedure == 'A':

        return math.sqrt((goal_coord.x - current_coord.x) **
                      2 + (goal_coord.y - current_coord.y)**2) / 2
    else:
        return 0


def graphsearch(input_map, flag, procedure_name):
    if procedure_name not in ['D', 'A']:
        raise Exception('invalid procedure name')
    # initialize open and closed list
    open_list=  OpenList(procedure_name)
    close_list = CloseList()

    # seq_counter count the order of expansion, which is used in defining identifier
    seq_counter = 0
    
    # find start node in map
    expansion_order = 1
    start_node = Node(seq_counter, None, None, input_map, 0, procedure_name, None)
    seq_counter += 1
    # expansion_order += 1

    # add start node to openlist
    open_list.add_children([start_node], close_list)

    # create bounding number of DLS, it is the number of normal tile in the map
    bound = input_map.get_normal_num() + 1
    # current_depth = 0
    while True:

        # nothing left to be expanded, then print out message and write message to output
        if len(open_list) == 0:
            return 'NO-PATH'
        next_expansion = open_list.pop()

        # goal test
        if next_expansion.is_goal():
            return next_expansion.get_path()
        
        # test if the bound has been reached in DLS
        if procedure_name == 'D' and next_expansion.node_depth == bound:
            continue
        close_list.add(next_expansion)
        generated_children, seq_counter = next_expansion.expand(close_list, seq_counter, procedure_name, expansion_order)
        expansion_order += 1
        open_list.add_children(generated_children, close_list)

        # print output in diagnose mode
        if int(flag) >= 1:
            expansion_node_info = "N{seq}\tg={g} h={h:.2f} f={f:.2f}".format(**vars(next_expansion))
            children_path_info = "Children:\t{"
            for i in generated_children:
                children_path_info += "N{seq}:{path}, ".format(seq=i.seq, path=i.get_path())
            children_path_info =children_path_info[:-2]
            children_path_info += '}'
            
            output_str = expansion_node_info +'\n'+ children_path_info+'\n' + str(open_list) + '\n' + str(close_list) + '\n'
            print(output_str)
            flag -= 1



def read_from_file(file_name):
    return Map(file_name)



###############################################################################
########### DO NOT CHANGE ANYTHING BELOW ######################################
###############################################################################

def write_to_file(file_name, solution):
    file_handle = open(file_name, 'w')
    file_handle.write(solution)

def main():
    # create a parser object
    parser = ap.ArgumentParser()

    # specify what arguments will be coming from the terminal/commandline
    parser.add_argument("input_file_name", help="specifies the name of the input file", type=str)
    parser.add_argument("output_file_name", help="specifies the name of the output file", type=str)
    parser.add_argument("flag", help="specifies the number of steps that should be printed", type=int)
    parser.add_argument("procedure_name", help="specifies the type of algorithm to be applied, can be D, A", type=str)


    # get all the arguments
    arguments = parser.parse_args()

##############################################################################
# these print statements are here to check if the arguments are correct.
#    print("The input_file_name is " + arguments.input_file_name)
#    print("The output_file_name is " + arguments.output_file_name)
#    print("The flag is " + str(arguments.flag))
#    print("The procedure_name is " + arguments.procedure_name)
##############################################################################

    # Extract the required arguments

    operating_system = platform.system()

    if operating_system == "Windows":
        input_file_name = arguments.input_file_name
        input_tokens = input_file_name.split("\\")
        if not re.match(r"(INPUT\\input)(\d)(.txt)", input_file_name):
            print("Error: input path should be of the format INPUT\input#.txt")
            return -1

        output_file_name = arguments.output_file_name
        output_tokens = output_file_name.split("\\")
        if not re.match(r"(OUTPUT\\output)(\d)(.txt)", output_file_name):
            print("Error: output path should be of the format OUTPUT\output#.txt")
            return -1
    else:
        input_file_name = arguments.input_file_name
        input_tokens = input_file_name.split("/")
        if not re.match(r"(INPUT/input)(\d)(.txt)", input_file_name):
            print("Error: input path should be of the format INPUT/input#.txt")
            return -1

        output_file_name = arguments.output_file_name
        output_tokens = output_file_name.split("/")
        if not re.match(r"(OUTPUT/output)(\d)(.txt)", output_file_name):
            print("Error: output path should be of the format OUTPUT/output#.txt")
            return -1

    flag = arguments.flag
    procedure_name = arguments.procedure_name


    try:
        input_map = read_from_file(input_file_name)  # get the map
    except FileNotFoundError:
        print("input file is not present")
        return -1
    solution_string = "" # contains solution
    write_flag = 0 # to control access to output file

    # take a decision based upon the procedure name
    if procedure_name == "D" or procedure_name == "A":
        solution_string = graphsearch(input_map, flag, procedure_name)
        write_flag = 1
    else:
        print("invalid procedure name")

    # call function write to file only in case we have a solution
    if write_flag == 1:
        write_to_file(output_file_name, solution_string)

if __name__ == "__main__":
    main()
