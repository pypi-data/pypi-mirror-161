# https://leetcode.com/problems/find-numbers-with-even-number-of-digits/

def even(arr):
    num = 0
    for a in arr:
        count = sum(1 for b in range(0, len(a)))
        if count % 2 == 0:
            num += 1
    print(num)




userInput = input("enter array of numbers\n")
arr = str.split(userInput)
even(arr)