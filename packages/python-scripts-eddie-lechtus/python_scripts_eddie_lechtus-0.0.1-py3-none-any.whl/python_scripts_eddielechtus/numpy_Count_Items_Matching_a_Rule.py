# https://leetcode.com/problems/count-items-matching-a-rule/
import numpy as np

# arr = np.array([["phone","blue","pixel"],["computer","silver","lenovo"],["silver","gold","iphone"], ["silver","silver","iphone"]])

# filter_arr = arr == 'silver'
# newarr = arr[filter_arr]
# print(filter_arr)
# print(newarr)

# shape = arr.shape
# dimensions = shape[0]
# count = 0
# for n in range(dimensions):
#     res = arr[n,1]
#     if res == 'silver':
#         count += 1
#         print(res)
#
# print(count)


arr = np.array([[1, 2, 5], [1, 2, 3]])
count = 0
n = 0
for idx, x in np.ndenumerate(arr):
  n += 1
  # print(idx, x)
  if idx[1] == 2:
      count += 1
      print("count :" + str(count), x)
