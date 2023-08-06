import re


def rem(s, p):
    res = True
    while res:
        res = re.search(p, s)
        s = re.sub(p, "", s)
    return s

string = "daabcbaabcbc"
pattern = "abc"
print(rem(string, pattern))