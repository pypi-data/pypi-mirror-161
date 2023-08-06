# https://leetcode.com/problems/check-if-the-sentence-is-pangram/

# return len(set(sentence)) == 26 # Number of Unqiue Characters Should Be 26


# uInput = input("enter string to check if Pangram\n")
# abc = "thequickbrownfoxjumpsoverthelazydog"
# has_all = all([char in uInput for char in abc])
# print(has_all)


uInput = input("enter string to check if Pangram\n")
abc = "thequickbrownfoxjumpsoverthelazydog"
if len(set(uInput)) == 26:
    print(set(uInput))
    res = -1
    for c in abc:
        if c in uInput:
            res = 1
        else:
            print("no")
            break
    if res == 1:
        print("yes")
else:
    print("not Pangram")