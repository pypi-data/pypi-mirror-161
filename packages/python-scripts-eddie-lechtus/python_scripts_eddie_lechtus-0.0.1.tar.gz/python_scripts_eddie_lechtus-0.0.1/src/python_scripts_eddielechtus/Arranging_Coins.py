# https://leetcode.com/problems/arranging-coins/


# def arrange(num):
#     coins = 0
#     levels = 0
#     intNum = int(num)
#     sumCoins = 0
#     for n in range(intNum):
#         if sumCoins < intNum - 1:
#             coins += 1
#             levels += 1
#             sumCoins = (coins * levels)
#             print("coins ", coins)
#             print("levels: ", levels)
#
# uInput = input("enter nu

class Solution:
    def arrangeCoins(self, n: int) -> int:
        i = 1
        while n>=i:
            n, i = n-i, i+1
        return i-1

uInput = input("enter number\n")
obj = Solution()
print(obj.arrangeCoins(int(uInput)))