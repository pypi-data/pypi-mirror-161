from Vehical import *

class Inputs:

    def __init__(self):
        self.userString = 'enter input with / without 7'
        self.userInput = ''
        self.sum = 1


    def BoomStr(self, userInput):
        print("str input")
        for x in userInput:
            if x == '7':
                print ("you entered : " + str(x) + " : " + str(self.sum) + " times")
                self.sum += 1
            else:
                print ("you entered : " + x)

    def BoomInt(self, userInput):
        print("int input")
        for x in str(userInput):
            if x == '7':
                print ("you entered : " + str(x) + " : " + str(self.sum) + " times")
                self.sum += 1
            else:
                print ("you entered : " + x)



obj = Inputs()
print (obj.userString)
obj.userInput = input()

# if obj.userInput.isdigit():
#     obj.BoomInt(obj.userInput)
# else:
#     obj.BoomStr(obj.userInput)

try:
    val = int(obj.userInput)
    obj.BoomInt(obj.userInput)
except:
    obj.BoomStr(obj.userInput)

VehicleObj = Vehicle(name="ford", max_speed=200, mileage=100)
print(VehicleObj.name, VehicleObj.max_speed, VehicleObj.mileage)


