from Vehical import *
class Bus(Vehicle):
    def seating_capacity(self, capacity=50):
        return super().seating_capacity(60)

class Car(Vehicle):
    pass

mybus = Bus("bus", 100, 200)
obj = Vehicle("school_bus", 100, 200)
var = obj.seating_capacity(100)
print(mybus.seating_capacity())
print(var)

mycar = Car("ford", 120, 40)
print(mycar.color, mycar.name, mycar.max_speed, mycar.mileage)
print(mybus.color, mybus.name, mybus.max_speed, mycar.mileage)

