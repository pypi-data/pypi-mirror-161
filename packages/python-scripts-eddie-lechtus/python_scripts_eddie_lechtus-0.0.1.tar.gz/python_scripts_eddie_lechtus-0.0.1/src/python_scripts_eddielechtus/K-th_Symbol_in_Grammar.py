import sys


def symbol(n, k, rows=['0']):
    newrows = []
    if n > 0:
        for i in range(len(rows)):
            if rows[i] == '0':
                newrows.extend('01')
            elif rows[i] == '1':
                newrows.extend('10')
        n -= 1
        symbol(n, k, newrows)

    print(rows)
    print(rows[k])
    sys.exit(0)


n = input("enter number of rows\n")
k = input("enter k-th element\n")
print(symbol(int(n)-1, int(k)-1))
