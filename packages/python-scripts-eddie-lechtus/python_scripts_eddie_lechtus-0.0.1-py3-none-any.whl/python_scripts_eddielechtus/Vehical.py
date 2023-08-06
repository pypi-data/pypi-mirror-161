class Vehicle:
    color = "white "

    def __init__(self, name, max_speed, mileage):
        self.name = name
        self.max_speed = max_speed
        self.mileage = mileage



    def seating_capacity(self, capacity):
        return f"The seating capacity of a {self.name} is {capacity} passengers"




class Bus(Vehicle):
    pass

mybus = Bus("volvo", 100, 20)
print("color : ", Vehicle.color, "name : ", mybus.name, "max_speed : ", mybus.max_speed, "millage : ", mybus.mileage)
