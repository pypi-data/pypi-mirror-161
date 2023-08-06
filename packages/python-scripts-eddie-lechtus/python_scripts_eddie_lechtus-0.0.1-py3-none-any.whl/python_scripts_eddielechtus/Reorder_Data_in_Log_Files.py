# https://leetcode.com/problems/reorder-data-in-log-files/
import re

arr_digits = []
arr_words = []
with open("log.txt") as file:
    txt = file.readline()
    print(txt)
    txt_split = txt.split(',')
    for t in txt_split:
        if re.search('^"dig.*"$', t):
             arr_digits.append(t)
        else:
             arr_words.append(t)
    print(arr_digits)
    print(arr_words)

str_dig = "".join(arr_digits)
str_word = "".join(arr_words)


with open("log_digits.txt", "w") as file:
    file.write(str_dig)
if file.closed:
    print(file.name, "closed")
    file = open("log_digits.txt", "r")
    txt = file.readline()
    print(file.name)
    print(txt)
    file.close()

with open("log_words.txt", "w") as file:
    file.write(str_word)
if file.closed:
    print(file.name, "closed")
    file = open("log_words.txt", "r")
    txt = file.readline()
    print(file.name)
    print(txt)
    file.close()