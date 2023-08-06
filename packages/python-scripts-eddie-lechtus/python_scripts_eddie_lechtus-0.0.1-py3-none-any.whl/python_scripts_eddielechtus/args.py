def args(*numbers):
    sumn = 0
    for n in numbers:
        sumn = sumn + n
    return ("sum : ", sumn)

print(args(1,2,3))