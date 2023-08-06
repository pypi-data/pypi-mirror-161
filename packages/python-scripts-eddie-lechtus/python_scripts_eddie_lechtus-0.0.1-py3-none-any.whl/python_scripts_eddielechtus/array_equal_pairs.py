# You are given an integer array nums consisting of 2 * n integers.
#
# You need to divide nums into n pairs such that:
#
# Each element belongs to exactly one pair.
# The elements present in a pair are equal.
# Return true if nums can be divided into n pairs, otherwise return false.

# Example 1:
#
# Input: nums = [3,2,3,2,2,2]
# Output: true
# Explanation:
# There are 6 elements in nums, so they should be divided into 6 / 2 = 3 pairs.
# If nums is divided into the pairs (2, 2), (3, 3), and (2, 2), it will satisfy all the conditions.

def pairs(nums):
    for num in nums:
        count = sum(1 for elem in nums if num == elem)
        if count % 2 > 0:
            return False

    return True

while True:
    nums = input("enter numbers 0-500. 'n' to stop\n")
    if nums == 'n':
        break
    elif not nums.isdigit():
        print("only digits allowed")
    elif 1 <= int(nums) <= 500:
        print("range is 0 to 500")
        break

print(pairs(nums))