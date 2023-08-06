# Given an binary array nums and an integer k, return true if all 1's are at least k places away from each other, otherwise return false.
import cProfile
import re


def kPlaces(userInput, target):
    ones = 0
    count = 0
    res = -1
    for i in userInput:
        if i == '1':
            ones += 1
            if ones > 1:
                  if int(target) <= count:
                    count = 0
                    ones = 1
                    res = 0
                    continue
                  else:
                    print("Fail! the gap is : " + str(count) + " less then target : " + target)
                    count = 0
                    ones = 1
                    res = -1
        else:
            count += 1


    if res != -1:
         return print("Success! all gaps match target")
    elif target == '1':
        return print("Fail! the gap is : " + str(count) + " less then target : " + target)
    elif target == '0':
        return print("Success! the gap is : " + str(count) + " target : " + target)

def main():
    while True:
        userInput = input('Enter 0 and 1 only. n to stop\n')
        if userInput == 'n':
            break
        elif '1' not in userInput:
            print("must be at least one '1' ")
        # elif any(c not in '01' for c in userInput):
        elif re.search('[^01]', userInput):
            print("only 0 or 1 allowed")
        else:
            target = input('Enter target\n')
            kPlaces(userInput, target)

if __name__ == '__main__':
    cProfile.run('main()')