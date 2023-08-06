def diff(arr):
    op = ['-', '+', '*', ':']
    n = len(arr)
    start = False
    c = 0

    for i in range(n):
        if arr[i].isdigit() and not start and c != 3:
            arr.insert(i, "(")
            start = True
            c += 1
        elif arr[i].isdigit() and start and c == 3:
            arr.insert(i+1, ")")
            start = False
            c = 0
        else:
            c += 1

    return arr


arr = ['2', '-', '1', '-', '1', '*', 5]
print(diff(arr))