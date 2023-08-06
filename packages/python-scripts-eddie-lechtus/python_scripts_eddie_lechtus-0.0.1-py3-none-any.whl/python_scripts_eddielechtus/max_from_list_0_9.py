import re


def calc(arr):
    biggest = 0
    newList = []
    for num in arr:
        num = int(num)
        if num > 0 and num < 10:
            newList.append(str(num))
    for num in newList:
        if re.search("[0-9]", num):
            num = int(num)
            if num > biggest:
                biggest = num
    return biggest


while True:
    userInput = input("enter numbers 1 and more digits. 'n' to stop\n")
    arr = userInput.split()
    # arr = list(map(int, arr))
    # print(type(arr))
    print(arr)
    print(calc(arr))
