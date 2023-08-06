

def palindromInt(num):
    temp = num
    n = 0
    while num > 0:
        dig = num % 10
        n = n * 10 + dig
        num = num // 10

    if n == temp:
        return True
    else:
        return False


ui = input("enter number\n")
print(palindromInt(int(ui)))
