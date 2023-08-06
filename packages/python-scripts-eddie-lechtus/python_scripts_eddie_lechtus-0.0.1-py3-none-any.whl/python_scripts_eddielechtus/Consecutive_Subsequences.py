from collections import Counter

flag = False
def con(arr):
    first = []
    n = len(arr)

    for i in range(n-1):
        if arr[i] < arr[i+1] and n - i >= 3:
            first.append(arr[i])
        elif i + 1 == n - 1 and arr[i] == arr[i+1]:
            first.append(arr[i])
    newarr = list((Counter(arr) - Counter(first)).elements())
    print(first)
    print(newarr)
    for j in range(len(newarr)-1):
        if newarr[j] < newarr[j+1]:
            global flag
            flag = True
        else:
            flag = False
            return flag

    return flag
print(con([1,2,3,3,4,4,5,5]))
# print(con([1,2,3,4,4,5]))