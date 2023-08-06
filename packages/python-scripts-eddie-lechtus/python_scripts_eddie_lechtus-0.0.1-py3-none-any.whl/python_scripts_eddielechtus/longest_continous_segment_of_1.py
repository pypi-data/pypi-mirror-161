# Given a binary string s, return true if the longest contiguous segment of 1's is strictly longer than the longest contiguous segment of 0's in s, or return false otherwise.
#
# For example, in s = "110100010" the longest continuous segment of 1s has length 2, and the longest continuous segment of 0s has length 3.
# Note that if there are no 0's, then the longest continuous segment of 0's is considered to have a length 0. The same applies if there is no 1's.
import cProfile

def longest1(userInput):
    c_one = 0
    c_zero = 0
    biggest_one = 0
    biggest_zero = 0
    for c in userInput:
        if c == '1':
            c_one += 1
            c_zero = 0
            if c_one > biggest_one:
                biggest_one = c_one
        else:
            c_zero += 1
            c_one = 0
            if c_zero > biggest_zero:
                biggest_zero = c_zero

    if biggest_one > biggest_zero:
        print("sequence of 1 bigger")
        return True
    else:
        print("sequence of 1 not bigger")
        return False


def main():
    while True:
        userInput = input("enter string of 0 or 1. 'n' to stop\n")
        if userInput == 'n':
            break
        elif any(c not in '01' for c in userInput):
            print("enter  0 or 1 only")
        else:
            print(longest1(userInput))

if __name__ == '__main__':
    cProfile.run('main()')
