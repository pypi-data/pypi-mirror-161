import sys


class HillsAndVallies:
    def __init__(self):
        self.hills = 0
        self.vallies = 0

    def valleyhill(self, start, end, nums: list) -> tuple:
        self.hill = None
        self.vallie = None

        for n in range(start, end):
            if start == len(nums) - 1:
                print(self.hills, self.vallies)
                sys.exit(0)
            elif int(nums[n]) > int(nums[n-1]):
                self.hill = True
            elif int(nums[n]) < int(nums[n-1]):
                self.vallie = True
            else:
                continue

            for j in range(n+1, len(nums)):
                if int(nums[j]) < int(nums[n]) and self.hill is True:
                        self.hills += 1
                        self.hill = False
                        if len(nums) - 1 != j:
                            self.valleyhill(j, len(nums) - 1, nums)
                        else:
                            start = j
                elif int(nums[j]) > int(nums[n]) and self.vallie is True:
                        self.vallies += 1
                        self.vallie = False
                        if len(nums) - 1 != j:
                            self.valleyhill(j, len(nums) - 1, nums)
                        else:
                            start = j
                else:
                    continue

        # return self.hills, self.vallies

obj = HillsAndVallies()
nums = [4, 2, 2, 5, 5, 3, 2, 4]
nums = list(map(str, nums))
obj.valleyhill(0, len(nums), nums)
