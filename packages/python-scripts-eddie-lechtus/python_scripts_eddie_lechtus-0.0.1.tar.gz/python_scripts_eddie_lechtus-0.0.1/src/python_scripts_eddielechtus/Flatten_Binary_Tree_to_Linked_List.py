class Node:
    def __init__(self, val=None):
        self.val = val
        self.left = None
        self.right = None
        self.next = None

    def push(self, node, val):
        if node is None:
            return Node(val)

        if val < node.val:
            node.left = self.push(node.left, val)
        else:
            node.right = self.push(node.right, val)

        return node

    def inorder(self, node, arr):
        if node is None:
            return
        if node is not None:
            try:
                self.inorder(node.left, arr)
                print("Tree node : ", node.val)
                arr.append(node)
                self.inorder(node.right, arr)
            except AttributeError as error:
                print(error)


        return arr

class LinkedList:
    def __init__(self):
        self.head = None

    def createList(self, node):
        arr = []
        obNode = Node()
        arrList = obNode.inorder(node, arr)
        self.head = arrList[0]
        headval = self.head
        print("Linked list Node : ", headval.val)
        for i in range(1, len(arrList)):
                headval.next = arrList[i]
                print("Linked list Node : ", headval.next.val)
                headval = headval.next

objNode = Node()
root = None
root = objNode.push(root, 1)
root = objNode.push(root, 20)
root = objNode.push(root, 3)
root = objNode.push(root, 40)
root = objNode.push(root, 5)
l_list = LinkedList()
l_list.createList(root)

