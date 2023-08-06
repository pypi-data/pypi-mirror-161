class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

class linkedList:
    def __init__(self):
        self.head = None

    def remove(self, n):
        prev = None
        printval = self.head
        # print(printval)
        while printval is not None:
            if printval.data == n:
                break
            prev = printval
            printval = printval.next
        print("removing : ", printval.data)
        prev.next = printval.next
        objLinkedList.listPrintOrig()

    def listPrintOrig(self):
        printval = self.head
        # print(printval)
        # print("printval.next : ", printval.next)
        while printval is not None:
            print(printval.data)
            printval = printval.next

    def reverseList(self):
        prev = None
        current = self.head
        while current is not None:
            next = current.next
            current.next = prev
            prev = current
            current = next

        # print(prev)
        self.head = prev

listNodes = []
objLinkedList = linkedList()
nodes = input("enter nodes\n")
nodes = nodes.split(" ")
target = input("enter target node from end\n")
for x in nodes:
    n = Node(x)
    listNodes.append(n)

# print("listNodes : ", listNodes)
objLinkedList.head = listNodes[0]
# print("objLinkedList.head : ", objLinkedList.head)
# print("len(listNodes) : ", len(listNodes))
for x in range(0, len(listNodes)):
    if x+1 != len(listNodes):
        # print("x : ", x)
        # print("x+1 : ", x + 1)
        node = listNodes[x]
        node.next = listNodes[x+1]
        # print("node.next: ", node.next)
    else:
        break

print("before reverse\n")
objLinkedList.listPrintOrig()
objLinkedList.reverseList()
print("after reverse\n")
objLinkedList.listPrintOrig()
objLinkedList.remove(target)