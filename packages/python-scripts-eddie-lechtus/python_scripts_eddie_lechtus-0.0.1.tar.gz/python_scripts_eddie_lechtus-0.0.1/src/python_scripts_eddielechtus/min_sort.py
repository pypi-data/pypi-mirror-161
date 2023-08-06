def min(numbers):
    minn = 0
    minnList = []
    for x in numbers:
        for y in numbers:
            if x < y:
                minn = x
            else:
                minn = y
        if minn not in minnList:
            minnList.append(minn)
    for a in numbers:
        if a not in minnList:
            minnList.append(a)
    return minnList


ui = input("enter numbers\n")
ui = ui.split(" ")
print(min(ui))