def alien(als, hs):
    for i in hs:
        for j in als:
            index_i = als.index(i)
            index_j = als.index(j)
            if index_i > index_j:
                print("f")
                flag = False
                break
            else:
                print("t")
                flag = True

    return flag



als = input("enter alien sequence\n")
hs = input("enter human string\n")
print(alien(als, hs))