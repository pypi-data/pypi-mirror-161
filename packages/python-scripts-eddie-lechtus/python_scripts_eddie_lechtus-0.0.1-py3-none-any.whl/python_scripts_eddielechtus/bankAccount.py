
class bankAccount:

    def __init__(self, account_number, owner, balance):
        self.account_number = int(account_number)
        self.owner = owner
        self.balance = int(balance)

    def deposit(self, amount, method):
        if method == 'y':
            self.balance = self.balance + amount
            return bankAccount.bankFees(accountObject.balance)

        elif (self.balance > amount):
            self.balance = self.balance - amount
            return accountObject.bankFees(accountObject.balance)
        else:
            print ("Balance is less then withdrawal amount")

    def bankFees(balance):
        balance -= balance * 0.5 / 100
        print("balance after fees applied : " + str(balance))

    def display(self):
        print (self.account_number, self.owner, self.balance)

    def methodCheck(self, method, amount):
        if method == 'y':
            print("Adding to account : " + amount)
        else:
            print("Withdrawing from account : " + amount)

    # def tst (self):
    #     print("tst")



accountObject = bankAccount(310628722, "Eddie Lechtus", 100)
accountObject.display()
method = input("Enter y To Add / Enter n to withdraw\n")
amount = input("Enter amount\n")
accountObject.methodCheck(method, amount)
accountObject.deposit(int(amount), method)

# accountObject.tst()
# bankAccount.tst("rr")



