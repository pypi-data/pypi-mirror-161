

def noDups(userInput):
    arr = set()
    for character in userInput:
        arr.add(character)

    print(sorted(arr))


userInput = input("enter string\n")
noDups(userInput)