def min():
    inList = (10, 2, 3, 100, 2000, 1, 3, -3, 1, 300)
    num = inList[0]
    for x in inList:
        if num > x:
            num = x
    return num

def max():
    inList = (10, 2, 3, 100, 2000, 1, 3, -3, 1, 300)
    num = inList[0]
    for x in inList:
        if num < x:
            num = x
    return num

print("minimum is : ", min())
print("maximum is : ", max())