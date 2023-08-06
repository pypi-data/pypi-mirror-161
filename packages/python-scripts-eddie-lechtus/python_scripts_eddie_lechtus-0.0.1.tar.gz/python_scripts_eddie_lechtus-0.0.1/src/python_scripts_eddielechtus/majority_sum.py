class Solution:
    def majorityElement(self, nums):
        majority_count = len(nums)//2
        for num in nums:
            count = sum(1 for elem in nums if elem == num)
            # print("count", count)
            if count > majority_count:
                return num


nums = [1, 1, 1, 4, 5, 6, 7, 8]
obj = Solution()
print(obj.majorityElement(nums))