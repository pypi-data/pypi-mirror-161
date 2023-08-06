def special(arr):
    s = [x for x in arr if x>= len(arr)]
    if len(s) >= len(arr):
        return len(s)
    else:
        return -1


arr = [2, 3, 5, 0]
print(special(arr))