import random 

def binarySearch(nums, low, high, target):

    if high >= low:

        mid = (high + low) // 2

        if nums[mid] == target:
            print(mid)

        elif nums[mid] > target:
            return binarySearch(nums, low, mid - 1, target)

        elif nums[mid] < target:
            return binarySearch(nums, mid + 1, high, target)

    else:
        return -1   
    



nums = sorted(random.sample(range(0, 10), 5))
# print(type(nums))
# nums = int(input("Enter numbers\n"))
# nums = [int (x) for x in str(nums)]
# nums = [int (x) for x in str(nums)]
target = int(input("Enter number to search 1-9\n"))
low = 0
high = len(nums)-1
res = binarySearch(nums, low, high, target)
if res == -1:
    print("number not in the list") 