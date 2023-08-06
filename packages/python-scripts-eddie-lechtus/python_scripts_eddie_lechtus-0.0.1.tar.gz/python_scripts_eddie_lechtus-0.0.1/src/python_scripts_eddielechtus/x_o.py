import re
import numpy as np

x_pattern = 'xxx'
zero_pattern = '000'
matrix = np.array([['-','a', 'b', 'c'], [1, '', '', ''], [2, '', '', ''], [3, '', '', '']])
cross = []
Flag = False
Player = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class game:

    def __init__(self):
        self.target = []


    def calculateInput(self):
        coordinates = []
        match self.target:
            case '1', 'a':
                coordinates = [1, 1]
            case '1', 'b':
                coordinates = [1, 2]
            case '1', 'c':
                coordinates = [1, 3]
            case '2', 'a':
                coordinates = [2, 1]
            case '2', 'b':
                coordinates = [2, 2]
            case '2', 'c':
                coordinates = [2, 3]
            case '3', 'a':
                coordinates = [3, 1]
            case '3', 'b':
                coordinates = [3, 2]
            case '3', 'c':
                coordinates = [3, 3]

        obj.convertInput(coordinates)


    def convertInput(self, coordinates):
        row = int(coordinates[0])
        column = int(coordinates[1])
        m = matrix[row, column]

        if m == 'x' or m == '0':
            print("coordinates taken")
            self.target = []
        else:
            obj.matchPlayer(coordinates, row, column)


    def matchPlayer(self, coordinates, row, column):
        global Player
        match Player:
            case False:
                    matrix[row, column] = 'x'
                    self.target = []
                    Player = True
                    obj.checkWin(coordinates)

            case True:
                    matrix[row, column] = '0'
                    self.target = []
                    Player = False
                    obj.checkWin(coordinates)



    def checkWin(self, coordinates):
        ro = matrix[coordinates[0], :]
        # print(type(ro))
        ro = np.delete(ro, 0)
        str_ro = ''.join([str(c) for c in ro])
        match_ro_x = re.search(x_pattern, str_ro)
        # print(match_ro_x)

        col = matrix[:, coordinates[1]]
        col = np.delete(col, 0)
        str_col = ''.join([str(c) for c in col])
        match_col_x = re.search(x_pattern, str_col)

        ro = matrix[coordinates[0], :]
        ro = np.delete(ro, 0)
        str_ro = ''.join([str(c) for c in ro])
        match_ro_zero = re.search(zero_pattern, str_ro)

        col = matrix[:, coordinates[1]]
        col = np.delete(col, 0)
        str_col = ''.join([str(c) for c in col])
        match_col_zero = re.search(zero_pattern, str_col)

        global cross
        cross.append(matrix[1, 1])
        cross.append(matrix[2, 2])
        cross.append(matrix[3, 3])
        str_cross = ''.join([str(c) for c in cross])
        match_cross1_x = re.search(x_pattern, str_cross)
        match_cross1_zero = re.search(zero_pattern, str_cross)

        cross.clear()
        cross.append(matrix[3, 1])
        cross.append(matrix[2, 2])
        cross.append(matrix[1, 3])
        str_cross2 = ''.join([str(c) for c in cross])
        match_cross2_x = re.search(x_pattern, str_cross2)
        match_cross2_zero = re.search(zero_pattern, str_cross2)


        if (match_ro_x is not None or match_col_x is not None):
                print("User with 'x' win!", bcolors.BOLD, bcolors.WARNING)
                obj.printResult()
        elif (match_ro_zero != None or match_col_zero != None):
                print("User with '0' win!", bcolors.BOLD, bcolors.WARNING)
                obj.printResult()
        elif (match_cross1_x != None or match_cross2_x != None):
            print("User with 'x' win!", bcolors.BOLD, bcolors.WARNING)
            obj.printResult()
        elif (match_cross1_zero != None or match_cross2_zero != None):
            print("User with 'x' win!", bcolors.BOLD, bcolors.WARNING)
            obj.printResult()
        else:
            print(matrix)


    def printResult(self):
        print(matrix)
        global Flag
        Flag = True


obj = game()
print(matrix)
print("Use coordinates. E.g : Row - 1 / Column - A is the top left 8.")
userInput = input("Enter 1 for coordinates to start or 'n' to quit\n")
while not Flag:
    match(userInput):
        case 'n':
            break
        case '1':
            row = input("Enter row 1-3\n")
            column = input("Enter column a-c \n")
            if not re.search('[^123]', row) and not re.search('[^abc]', column):
                 obj.target.append(row)
                 obj.target.append(column)
                 obj.calculateInput()
            else:
                print("Wrong input range. Try again")


