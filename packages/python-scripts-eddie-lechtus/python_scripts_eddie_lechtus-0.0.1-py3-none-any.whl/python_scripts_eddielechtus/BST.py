class BSTnode:
    def __init__(self, key=None):
        self.key = key
        self.left = None
        self.right = None

    def insert(self, node, key):
        if node is None:
            return BSTnode(key)

        if self.key == key:
            return

        if key < node.key:
            node.left = self.insert(node.left, key)
        else:
            node.right = self.insert(node.right, key)

        return node

    def inorder(self, root):
        if root is not None:
            self.inorder(root.left)
            print(str(root.key) + "->", end=' ')
            self.inorder(root.right)


obj = BSTnode()
root = None
root = obj.insert(root, 8)
root = obj.insert(root, 3)
root = obj.insert(root, 1)
root = obj.insert(root, 6)
root = obj.insert(root, 7)
root = obj.insert(root, 10)
root = obj.insert(root, 14)
root = obj.insert(root, 4)

obj.inorder(root)
