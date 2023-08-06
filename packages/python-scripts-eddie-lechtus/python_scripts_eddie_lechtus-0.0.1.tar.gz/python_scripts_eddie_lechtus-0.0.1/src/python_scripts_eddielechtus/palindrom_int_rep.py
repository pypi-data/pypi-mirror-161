import cProfile

def palindrom(num):
    temp = num
    rev = 0

    while (num > 0):
        dig = num % 10
        rev = rev * 10 + dig
        num = num // 10

    if temp != rev:
        return -1


def main():
    repeat = True
    while repeat:
        try:
            num = int(input("Enter number\n"))
            repeat = False
        except ValueError:
            print("only numbers allowed")
            # raise Exception("only numbers allowed")

    if num > 0:
        res = palindrom(num)
        # cProfile.run(res)
    else:
        print("cant be negative")

    if res != -1:
        print("Palindrom!")
    else:
        print("Not a palindrom")


if __name__ == '__main__':
    cProfile.run('main()')