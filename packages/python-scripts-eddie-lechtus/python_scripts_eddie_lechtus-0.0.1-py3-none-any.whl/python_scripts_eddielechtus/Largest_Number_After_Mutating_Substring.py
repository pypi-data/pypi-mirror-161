import random


def check(num, i, change):
    numList = []
    numList[:0] = num
    elem = numList[i]
    elem = int(elem)

    if numList[i] < change[elem]:
        numList[i] = change[elem]
    else:
        return int(num)

    numStr = "".join(x for x in numList)
    return int(numStr)

def  largest(num:str, change:list):
    for i in range(len(num)):
        res = check(str(num), i, change)
        # print(res)
        if int(num) < res:
            num = res

    return num

nn = [random.randint(1, 1000) for x in range(10)]
print(nn)

# for j in range(10):
#     n = (random.randint(1, 1000))
#     nn.append(n)
#     print(nn)

change_nums = ["9","8","5","0","3","6","4","2","6","8"]
for i in range(10):
    print(largest(str(nn[i]), change_nums))