def multiplication(n):
    def multiplier(x):
        return n * x
    return multiplier

print("enter multiplication value ")
multiplicationValue = int(input())
print("enter multiplier value ")
multiplierValue = int(input())
result = multiplication(multiplicationValue)
print(result(multiplierValue))
