def remove_duplicates(value):
    var=""
    for i in value:
        if i in value:
            if i in var:
                pass
            else:
                var=var+i
    return var

print(remove_duplicates("11223445566666ababzzz@@@123#*#*"))

# mylist = ["ABA", "CAA", "ADA"]
# results = []
# for item in mylist:
#     buffer = []
#     for char in item:
#         if char not in buffer:
#             buffer.append(char)
#     results.append("".join(buffer))
#
# print(results)

# output
# ABA
# CAA
# ADA
# ['AB', 'CA', 'AD']

# import re
# pattern = r'(.)\1+' # (.)
# any character repeated (\+) more than
# repl = r'\1'        # replace it once
# text = 'shhhhh!!!'
# print(re.sub(pattern,repl,text))


foo='mppmtaa'
# print(''.join(set(foo)))
print(''.join([j for i,j in enumerate(foo) if j not in foo[:i]]))
