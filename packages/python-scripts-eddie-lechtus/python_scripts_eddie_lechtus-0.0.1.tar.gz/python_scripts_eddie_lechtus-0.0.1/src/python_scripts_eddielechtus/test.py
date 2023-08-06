def myFun(*argv):
    for arg in argv:
        print(arg)

    a = {1:'a',2:'b',3:'c'}
    b = {4:'d',5:'e',6:'f'}
    l1 = [1, 2, 3]
    l2 = ['l', 'l', 'l']
    # d = {**a, **b}
    zd = {}
    # zd = dict.fromkeys(l1, l2)
    # zd = dict(zip(l1, l2))
    for i in range(4, 7):
        zd[i] = b[i]
    print(zd)
    # print(b[4])
    # a.update(b)
    # print(a)

myFun('Hello', 'Welcome', 'to', 'GeeksforGeeks')