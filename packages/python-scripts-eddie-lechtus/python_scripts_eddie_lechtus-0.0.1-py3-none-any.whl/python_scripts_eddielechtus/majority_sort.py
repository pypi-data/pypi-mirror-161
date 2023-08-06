nums = [1, 1, 1, 1, 3, 4, 5]
class Solution:
    def majorityElement(self, nums):
        nums.sort()
        return nums[len(nums)//2]


obj = Solution()
print(obj.majorityElement(nums))