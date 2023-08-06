import argparse
import cProfile


def good(string):
    counter = 0
    s1 = []
    arr = [c for c in string]
    for i in range(len(arr)):
        s1.extend(arr[i])
        s2 = arr[i+1:]
        counter_s1 = [j for j in s1 if j not in s2]
        counter_s2 = [a for a in s2 if a not in s1]
        if len(counter_s1) == len(counter_s2) and len(counter_s1) != 0 and len(counter_s2) != 0:
            counter += 1
            print(f'good string are {s1} and {s2}\n')

    return counter


print(good('aacaba'))

# def main():
#     parser = argparse.ArgumentParser(description='good string')
#     parser.add_argument('--s', type=str, required=True, help='string for finding number of 2 good splits')
#     args= parser.parse_args()
#     print(good(args.s))
#
#
# if __name__ == '__main__':
#     cProfile.run('main()')