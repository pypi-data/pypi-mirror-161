# Given
# an
# integer
# x,
# return true if x is palindrome
# integer.
#
# An
# integer is a
# palindrome
# when
# it
# reads
# the
# same
# backward as forward.
#
# For
# example, 121 is a
# palindrome
# while 123 is not.
#
# Example
# 1:
#
# Input: x = 121
# Output: true
# Explanation: 121
# reads as 121
# from left to
#
# right and
# from right to
#
# left.
# Example
# 2:
#
# Input: x = -121
# Output: false
# Explanation: From
# left
# to
# right, it
# reads - 121.
# From
# right
# to
# left, it
# becomes
# 121 -.Therefore
# it is not a
# palindrome.
# Example
# 3:
#
# Input: x = 10
# Output: false
# Explanation: Reads
# 01
# from right to
#
# left.Therefore
# it is not a
# palindrome.
#
# Constraints:
#
# -231 <= x <= 231 - 1

def palindrom(x):

    # STR 1
    l = len(x) - 1

    for i in range(0, l):
        start = x[i]
        end = x[l]

        # print("i : ", type(x[i]))
        # print("l : ", type(x[l]))
        # print("int(x[i])", type(start))
        # print("int(x[l])", type(end))

        if start != end:
            return -1
            break
        else:
            l -= 1
            continue

    # STR 2
    # print(x[::-1])
    # if x == x[::-1]:
    #     return 1
    # else:
    #     return -1



x = input("enter number\n")
# print(type(x))
if 0 < int(x) <= 2147483648:
    res = palindrom(x)
else:
    print("wrong range of 2147483648")

if res == -1:
    print("not a palindrom number\n")
else:
    print("palindrom number\n")

