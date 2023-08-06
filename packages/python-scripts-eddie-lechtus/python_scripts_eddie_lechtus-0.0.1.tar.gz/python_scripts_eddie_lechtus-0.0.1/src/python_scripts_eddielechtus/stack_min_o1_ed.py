
class stack:

    def __init__(self):
        self.array = []
        self.top = -1
        self.max = 100

    def isEmpty(self):
        if self.top == -1:
            return True
        else:
            return False

    def isFull(self):
        if self.top == self.max - 1:
            return True
        else:
            return False

    def push(self, data):
        if self.isFull():
            print("Stack full")
            return
        else:
            self.top += 1
            self.array.append(data)

    def pop(self):
        if self.isEmpty():
            print("Stack empty")
            return
        else:
            self.top -= 1
            return self.array.pop()


class SpecialStack(stack):


    def __init__(self):
        super().__init__()
        self.Min = stack()

    def push(self, x):
        if self.isEmpty():
            super().push(x)
            self.Min.push(x)
        else:
            super().push(x)
            y = self.Min.pop()
            self.Min.push(y)
            if x < y:
                self.Min.push(x)
            else:
                self.Min.push(y)

    # def pop(self):
    #     x = super().pop()
    #     self.Min.pop()
    #     print("pop2")
    #     return x

    def getMin(self):
        x = self.Min.pop()
        self.Min.push(x)
        return x

if __name__ == '__main__':
    obj = SpecialStack()
    while True:
        userInput = input("Enter number ot 'n' to stop \n")
        if userInput == 'n':
            break
        else:
            obj.push(userInput)

    print(obj.getMin())















