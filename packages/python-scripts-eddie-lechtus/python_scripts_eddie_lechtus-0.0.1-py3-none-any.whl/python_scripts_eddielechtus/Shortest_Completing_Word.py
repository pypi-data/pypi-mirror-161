# https://leetcode.com/problems/shortest-completing-word/
import re

lp = "1s3 PSt"
def shortest_completing_word(lp, arr):
    counted = []
    lp = re.split("[^a-zA-Z]*", lp)
    for a in arr:
        count = 0
        for b in a:
            if any(c in lp for c in b):
                count += 1

        counted.append(count)

    maxCounted = max(counted)
    maxCountedList = []
    maxCountedList.append(maxCounted)
    res = next((ele for ele in iter(counted) if ele in maxCountedList), None)
    maxCountedIndex = counted.index(res)
    print("Completing word is : ", arr[maxCountedIndex])

    # for m in counted:
    #     if m == maxCounted:
    #         maxCountedIndex = counted.index(maxCounted)
    #         print("Completing word is : ", arr[maxCountedIndex])
    #         break




while True:
    print("LicensePlate: %s. Enter 1 to change LisencePlate. 2 to run. 'n' to quit" % lp)
    userInput = input("Enter choice\n")
    match userInput:
        case 'n':
            break
        case '1':
           lp = input("Enter new LicensePlate\n")
           continue
        case '2':
            s = input("Enter words\n")
            arr = s.split()
            arr.sort(key=len)
            print(arr)
            shortest_completing_word(lp, arr)

