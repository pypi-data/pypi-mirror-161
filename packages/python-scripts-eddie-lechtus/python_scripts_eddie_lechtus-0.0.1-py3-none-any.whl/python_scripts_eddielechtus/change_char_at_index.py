def replace(word, char, index):
    arr = []
    for c in word:
         arr.append(c)

    arr[int(index)] = char
    replacedWord = "".join(arr)
    print(replacedWord)


while True:
    userInput = input("enter 1 for replace. 'n' to stop\n")
    match userInput:
        case 'n':
            break
        case '1':
            word = input("enter word\n")
            char = input("enter char\n")
            index = input("enter index\n")
            if int(index) <= len(word):
                 replace(word, char, index)
            else:
                print("wrong index. try again\n")
