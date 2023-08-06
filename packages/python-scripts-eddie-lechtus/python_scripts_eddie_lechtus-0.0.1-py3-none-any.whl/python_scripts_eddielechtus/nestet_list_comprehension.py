def nested(numbers):
    val = 0
    mindiff = [val for val in numbers for y in numbers if int(val) < int(y)]
    return min(mindiff), mindiff


ui = input("enter numbers\n")
list = ui.split(' ')
print(type(list))
print(nested(list))