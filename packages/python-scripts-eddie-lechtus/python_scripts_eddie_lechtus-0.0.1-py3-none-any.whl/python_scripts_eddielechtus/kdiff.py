import argparse
import cProfile

class dif:
    def __init__(self, knum=None):
        self.knum = knum

    def positive(self, x):
        if x < 0:
            return ("k number must be > 0")

    def genCheck(self, x, y, n):
        res = False
        if x >= 0 and y < n:
            res = True
        elif x != y:
            res = True
        yield res

    # @positive
    def kdiff(self, k, arr):
        n = len(arr)
        count = 0
        s1 = []

        for i in range(n):
            for j in range(1, n):
                res = self.genCheck(j, i, n)
                s2 = [arr[i], arr[j]]
                if res and abs(arr[j] - arr[i]) == k and s2 not in s1:
                    s1.append(s2)
                    count += 1

        return s1, count

# def main():
#     parser = argparse.ArgumentParser(description='https://leetcode.com/problems/k-diff-pairs-in-an-array/')
#     parser.add_argument('--list', type=int, nargs="+", help='Enter numbers only', required=True)
#     parser.add_argument('--k', type=int, help='Enter k number', required=True)
#     args = parser.parse_args()
#     obj = kdiff(args.k)
#     print(f'For {args.list} and {args.k} number:\n')
#     print(kdiff(args.k, args.list))
#
# if __name__ == '__main__':
#     cProfile.run('main()')

parser = argparse.ArgumentParser(description='https://leetcode.com/problems/k-diff-pairs-in-an-array/')
parser.add_argument('--list', type=int, nargs="+", help='Enter numbers only', required=True)
parser.add_argument('--k', type=int, help='Enter k number', required=True)
args = parser.parse_args()
obj = dif(args.k)
print(f'For {args.list} and {args.k} number:\n')
print(obj.kdiff(args.k, args.list))
