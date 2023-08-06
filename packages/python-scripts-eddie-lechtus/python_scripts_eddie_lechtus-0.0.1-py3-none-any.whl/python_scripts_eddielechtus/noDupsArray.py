class Solution(object):
    def noDupsArray(self, arr):
        dic = {}

        for i in range(0, len(arr)):
             dic[arr[i]] = arr[i]
        # print(dic)

        keys = list(dic)
        return print("no dups : ", keys)

arr = input("Enter nmbers\n")
obj = Solution()
obj.noDupsArray(arr)