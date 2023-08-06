# https://www.my-courses.net/2020/02/exercises-with-solutions-on-oop-object.html

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        return (self.name, self.age)

class Student(Person):
    def __init__(self, name, age, section):
        Person.__init__(self, name, age)
        self.section = section

    def displayStudent(self):
        return (self.name, self.age, self.section)

    def test(self):
        print("objStudent: ", objStudent.name)

obj = Person("edd", 41)
print(obj.display())

objStudent = Student("stam", 33, "science")
print(objStudent.displayStudent())
objStudent.test()

str = obj.name = "tst"
print(str)
