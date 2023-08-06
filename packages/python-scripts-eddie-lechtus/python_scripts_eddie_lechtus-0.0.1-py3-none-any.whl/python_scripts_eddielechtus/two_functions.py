def f1 (a):
    return f2(a)

def f2 (a):
    b = input("enter another number\n")
    res = int(a) * int(b)
    return res

a = input("enter number\n")
print(f1(a))