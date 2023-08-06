def bubble(arr):
    swapped = False
    n = len(arr)

    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                swapped = True
                arr[j], arr[j+1] = arr[j+1], arr[j]

        if not swapped:
                return ("no swappe needed\n")
    return arr

arr = [1, 3, 2, 5, 4, 6, 7, 8, 22, 11, 12, 33, 21]
print(bubble(arr))