import re

import pandas as pd

# columns = [0, 1, 2, 3, 4, 5, 6, 7]
from pandas.compat import numpy

chess = {
    "0": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "1": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "2": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "3": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "4": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "5": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "6": ['-', '-', '-', '-', '-', '-', '-', '-'],
    "7": ['-', '-', '-', '-', '-', '-', '-', '-'],
}

df = pd.DataFrame(chess)
print(df.to_string())
print("==========================")
Flag = False

class officer:

    def __init__(self, row, col):
        self.row = row
        self.col = col


    def calcUp1(self):
        column = obj.col
        column = int(column)
        row_ = obj.row
        row_ = int(row_)
        df.loc[row_, str(column)] = '*'
        for r in range(row_, 7):
            pos = df.loc[row_, obj.col]
            NaN = pos != pos
            if NaN:
                Flag = True
            else:
                Flag = False
            print(NaN)
            column += 1
            row_ -= 1
            if row_ > 7 or row_ < 0:
                Flag = True
            if column > 7 or column < 0:
                Flag = True

            match Flag:
                case False:
                    df.loc[row_, str(column)] = '*'
                    print("row : ", row_)
                    print("col : ", column)
                case True:
                    break

    def calcDown1(self):
        column = obj.col
        column = int(column)
        row_ = obj.row
        row_ = int(row_)
        df.loc[row_, str(column)] = '*'
        for r in range(0, row_):
            pos = df.loc[row_, obj.col]
            NaN = pos != pos
            if NaN:
                Flag = True
            else:
                Flag = False
            print(NaN)
            column -= 1
            row_ += 1
            if row_ > 7 or row_ < 0:
                Flag = True
            if column > 7 or column < 0:
                Flag = True

            match Flag:
                case False:
                    df.loc[row_, str(column)] = '*'
                    print("row : ", row_)
                    print("col : ", column)
                case True:
                    break


    def calcUp2(self):
        column = obj.col
        column = int(column)
        row_ = obj.row
        row_ = int(row_)
        df.loc[row_, str(column)] = '*'
        for r in range(0, row_):
            pos = df.loc[row_, obj.col]
            NaN = pos != pos
            if NaN:
                Flag = True
            else:
                Flag = False
            print(NaN)
            column -= 1
            row_ -= 1
            if row_ > 7 or row_ < 0:
                Flag = True
            if column > 7 or column < 0:
                Flag = True

            match Flag:
                case False:
                    df.loc[row_, str(column)] = '*'
                    print("row : ", row_)
                    print("col : ", column)
                case True:
                    break

    def calcDown2(self):
        column = obj.col
        column = int(column)
        row_ = obj.row
        row_ = int(row_)
        df.loc[row_, str(column)] = '*'
        for r in range(row_, 7):
            pos = df.loc[row_, obj.col]
            NaN = pos != pos
            if NaN:
                Flag = True
            else:
                Flag = False
            print(NaN)
            column += 1
            row_ += 1
            if row_ > 7 or row_ < 0:
                Flag = True
            if column > 7 or column < 0:
                Flag = True

            match Flag:
                case False:
                    df.loc[row_, str(column)] = '*'
                    print("row : ", row_)
                    print("col : ", column)
                case True:
                    break


        print(df.to_string())


while True:
    userInput = input("1 to enter officer position or 'n' to quit\n")
    match userInput:
        case 'n':
            break
        case '1':
            row = input("enter row\n")
            if re.search("[0-7]", row):
                col = input("enter col\n")
                if re.search("[0-7]", col):
                     obj = officer(row=row, col=col)
                     obj.calcUp1()
                     obj.calcDown1()
                     obj.calcUp2()
                     obj.calcDown2()
                else:
                    print("wrong column input. try again")
            else:
                print("wrong row input. try again")


