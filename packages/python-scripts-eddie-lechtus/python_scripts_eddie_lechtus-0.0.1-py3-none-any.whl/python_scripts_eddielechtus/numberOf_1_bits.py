import cProfile

class Solution:

    def __init__(self):
        self.check = 0

    def numberOf1(self, txt):
        self.check += 1
        count = 0
        for i in txt:
            if i == '1':
                count += 1


        return count


    def checkInput(self, userInput):
        for i in userInput:
            if i != '0' and i != '1':
                print("only 0 or 1 allowed")
            elif self.check == 0:
                print(obj.numberOf1(userInput))


def main():
    while True:
        userInput = input("Enter bits. 'n' to stop\n")
        if userInput == 'n':
            break
        else:
            obj.checkInput(userInput)



if __name__ == '__main__':
    obj = Solution()
    cProfile.run('main()')
