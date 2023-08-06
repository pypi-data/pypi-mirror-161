import numpy as np

nums = [[7, 6, 3, 4], [6, 7, 3, 4]]
final = []
l = []
inter = set(nums[0])
for li in range(1, len(nums)):
    s = set(nums[li])
    final = inter & s

print(final)
