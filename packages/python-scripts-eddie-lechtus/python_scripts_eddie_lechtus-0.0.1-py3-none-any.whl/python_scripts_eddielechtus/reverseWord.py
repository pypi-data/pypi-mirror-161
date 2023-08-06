def reverseWordsEx1():
    strToReverse = input("Enter words to reverse\n")
    return ' '.join(x[::-1] for x in strToReverse.split(" "))

def reverseWordsEx2():
    word = input("enter word to reverse\n")
    return word[::-1]

print("reversed : ", reverseWordsEx1())
print("reversed word : ", reverseWordsEx2())

