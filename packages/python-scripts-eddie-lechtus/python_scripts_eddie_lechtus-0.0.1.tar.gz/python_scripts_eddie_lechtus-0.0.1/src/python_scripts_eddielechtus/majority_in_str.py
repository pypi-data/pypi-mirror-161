# Given an array nums of size n, return the majority element.
#
# The majority element is the element that appears more than ⌊n / 2⌋ times. You may assume that the majority element always exists in the array.
#
import cProfile


def majority(arr):
    checkList = []
    count = 0
    max = 0
    res = 0
    # string = 'abc'
    # for s in string:
    #     print(s)
    # for s in range(0, len(string)):
    #     print("s : ", s)
    #     print("string[s] ", string[s])
    # num = range(1, 10)
    # for n in num:
    #     print(n)
    for i in range(0, len(arr)):
        if str(i) not in checkList:
            for j in range(i + 1, len(arr)):
                if arr[i] == arr[j]:
                    print("arr[i] : ", arr[i])
                    print("arr[j] : ", arr[j])
                    print("i : ", i)
                    print("j : ", i)
                    count += 1
                    checkList.append(arr[i])
            if max < count:
                res = arr[i]
                max = count + 1
                count = 0

    return print("number : " + str(res) + " at max occurrences : " + str(max))


def main():

    while True:
        userInput = input("enter numbers. 'n' to stop\n")
        if userInput == 'n':
            break
        if userInput.isdigit():
            # print(userInput)
            # arr = str.split(userInput)
            # print(arr)
            majority(userInput)
        else:
            print("only digits")


if __name__ == '__main__':
    cProfile.run('main()')