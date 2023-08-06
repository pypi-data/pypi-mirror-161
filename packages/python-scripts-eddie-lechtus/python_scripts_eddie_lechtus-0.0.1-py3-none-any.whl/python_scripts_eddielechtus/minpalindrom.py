from collections import Counter


def minpalindrom(st):
    st = list(st)
    l = []
    ml = []
    checkl = []
    m = 0
    count = 1

    for a in range(len(st) - 1, -1, -1):
        checkl.append(st[a])
    if checkl == st:
        return 1

    while len(st) > 1:
      for i in st:
          l.append(i)
          if l[::-1] == l:
              c = len(l)
              if m < c:
                  m = c
                  ml = l.copy()
      #             print("ml", ml)
      # print("l", l)
      # newl = [x for x in l if x not in ml]
      # newl = filter(lambda x: x not in ml, l)
      newl = list((Counter(l) - Counter(ml)).elements())
      count += 1
      st = newl.copy()
      minpalindrom(st)

    return count

#s = "b"
s = "baabb"
#s = "baab"
print(minpalindrom(s))
