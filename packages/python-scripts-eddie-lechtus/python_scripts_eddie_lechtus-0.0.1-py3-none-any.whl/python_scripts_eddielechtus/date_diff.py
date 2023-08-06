import datetime

def datediff(date1, date2):
    year1 = int(date1[:4])
    year2 = int(date2[:4])
    month1 = int(date1[5:7])
    month2 = int(date2[5:7])
    day1 = int(date1[8:])
    day2 = int(date2[8:])
    x1 = datetime.datetime(year1, month1, day1)
    print("x1", x1)
    x2 = datetime.datetime(year2, month2, day2)
    print("x2", x2)
    return abs((x2 - x1).days)

d1 = input("enter first date\n")
d2 = input("enter second date\n")
print(datediff(d1, d2))