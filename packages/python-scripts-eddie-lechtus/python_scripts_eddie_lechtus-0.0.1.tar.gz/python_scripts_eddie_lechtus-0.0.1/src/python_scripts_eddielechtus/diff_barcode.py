import random
def diff(bar):
    difflist = []
    flag = True
    while flag:
        for i in bar:
            npos = random.randint(0 , len(bar))
            difflist.insert(npos, i)
        if difflist == bar:
            flag = False
            print("same")
        else:
            print("different")
            break

    yield difflist

prev = []
uib = input("enter barcode\n")
for i in range(3):
    for res in diff(uib):
        if prev != res:
            prev = res
            print(res)
        else:
            prev = res