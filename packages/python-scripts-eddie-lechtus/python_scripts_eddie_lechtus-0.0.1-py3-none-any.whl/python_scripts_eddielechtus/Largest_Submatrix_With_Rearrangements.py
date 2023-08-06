from random import random, randint

import numpy as np
import pandas as pd

def genRandom():
    num = randint(0,1)
    yield num


def createArray(elements, rows, columns):
    a = np.empty((0), int)
    for x in range(elements):
        num = genRandom()
        num = next(num)
        a = np.append(a, [num])
    a = a.reshape(rows, columns)

    print('The Matrix\n')
    print(f'{a}\n')
    print("=============\n")
    print(rearrange(a, rows, columns))

def rearrange(matrix, rows, columns):
    matrix = np.sort(matrix)
    largest = 0
    sumRow = 0
    rowC = 0
    print('The Sorted Matrix\n')
    print(f'{matrix}\n')


    for i in range(rows-1):
        axSum = np.sum(matrix, axis=1) # get maximum of each row
        # idxSum = matrix.sum(axis=1).argmax() # get index of max row
    print(axSum)
    # print(idxSum)
    # for j in range(len(axSum)-1):
    #     largest += axSum[j]
    #     if axSum[j+1] < axSum[j]:
    #       return (f'The largest submatrix is of {largest} elements\n')

    # for idx, x in np.ndenumerate(matrix):
    #     print(idx, x)
    #     if x == 1:
    #         np.append(newMatrix, [])

    with np.nditer(matrix, op_flags=['readwrite'], order='C') as cell:
        # print("cell", cell)
        for x in cell:
            # print("x", x)
            while rowC <= columns:
                sumRow += x
                rowC += 1
            rowC = 0
            if largest < sumRow:
               largest = sumRow
            else:
                print("largest" , largest)

def rowsColumnsCalc(elements):
    suggestions = []
    for columns in range(1, 10):
        reminder = elements % columns
        if reminder == 0:
            rows = elements // columns
            suggestions.append([rows, columns])
    df = pd.DataFrame(suggestions, columns=['rows', 'columns'])
    return df


elements = input("Enter number of elements\n")
suggestion = rowsColumnsCalc(int(elements))
print('The suggested shape is :\n')
print(suggestion)
idx = input('Choose index to start\n')
u_idx = suggestion.loc[int(idx)]
createArray(int(elements), u_idx[0], u_idx[1])




