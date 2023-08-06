import os
import re
import sys
from collections import Counter
from datetime import time

def genRes(items, m):
    mlist = [i for i in items if i[1] == m]
    for j in mlist:
        yield j


def decorator(*args, **kwargs):
     print(os.system.__name__)

# @decorator
def frequency(words, k):
    c = Counter(words)
    items = c.items()
    m = max(c.values())
    count = 0

    # mlist = [i for i in items if i[1] == m]
    # for x in mlist:
    #     while count < k:
    #         print(x)
    #         count += 1

    for res in genRes(items, m):
        if count < k:
            print(res)
            count += 1



words = ["i","love","leetcode","i","love","coding"]
k = 1
frequency(words, k)