class Stack:

    def __init__(self):
        self.buttom = -1
        self.top = 100
        self.numbers = []
        self.min = []

    def isEmpty(self):
        if self.buttom == -1:
            return True
        else:
            return False

    def isFull(self):
        if self.buttom == self.top - 1:
            return True
        else:
            return False

    def pop(self):
        num = self.numbers.pop()
        self.numbers.append(num)
        self.top -= 1
        return num

    def append(self, num):
        self.numbers.append(num)

    def minCheck(self, number):
        if self.isFull():
            print("stack full")
        elif obj.isEmpty():
            self.numbers.append(number)
            self.min.append(number)
            self.buttom += 1
        else:
            num = obj.pop()
            obj.append(num)
            if number < num:
                self.min.append(number)
                self.numbers.append(number)
                self.buttom += 1
                # for x in self.numbers:
                #     print(x)
                # for x in self.min:
                #     print(x)
            else:
                self.min.append(num)
                self.numbers.append(num)
                self.buttom += 1
                # for x in self.numbers:
                #     print(x)
                # for x in self.min:
                #     print(x)

    def getMin(self):
        min = self.min.pop()
        print("numbers", self.numbers)
        print("min", self.min)
        print(min)


# if __name__ == '__main__':
obj = Stack()
while True:
    userInput = input("Enter number or 'n' to stop\n")
    if userInput == "n":
        obj.getMin()
        break
    else:
        obj.minCheck(userInput)


