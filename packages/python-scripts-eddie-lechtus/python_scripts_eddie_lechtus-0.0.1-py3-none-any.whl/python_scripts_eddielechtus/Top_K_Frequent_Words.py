import re
from collections import Counter

class Kf:
    def __init__(self, words):
        self.words = words

    def decorator(self, *args, **kwargs):
         def checkWords(func):
            check = re.findall('[0-9]', kwargs['words'])
            if check:
                return ("digits found")
            func()

         return checkWords()

    @decorator(words="12")
    def frequency(self, object, k):
        c = Counter(object.words)
        items = c.items()
        m = max(c.values())
        count = 0

        mlist = [i for i in items if i[1] == m]
        for x in mlist:
            while count < k:
                print(x)
                count += 1



words = ["i","love","leetcode","i","love","coding"]
k = 1
obKF = Kf(words)
obKF.frequency(obKF, k)