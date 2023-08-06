import argparse
import os
import re
from colorama import Fore, Back, Style
from termcolor import colored, cprint


def main(run, display, path, string):

    try:
        if args.e:
            os.system(f'python {script}')
        elif args.d:
                os.system(f'cat {script}')
        elif args.l:
            print(scripts_d)
        elif args.s:
            search_string(string)
        else:
            print("Wrong Input")
    except Exception as error:
        print(error)


def search_string(string):
    for file in dir_list:
        if os.path.isfile(file):
            try:
                f = open(file, 'r')
                data = f.read()
                if string in data:
                    print(colored(f"Found {string} in file {file}", 'red'))
                else:
                    pass
                    # print(f"{string} not found in {file}")
                f.close()
            except Exception as error:
                print(f'{error} at {file}')
        else:
            print(f"{file} not a file")

# def maybe_str_or_int(arg):
#     try:
#         return str(arg)
#     except ValueError:
#         pass


#Driver Code
dir_list = os.listdir()
scripts_d = {}
for i in range(len(dir_list)):
    scripts_d[i] = dir_list[i]

for count, filename in enumerate(dir_list):
    src = filename
    dst = filename.replace(' ', '_')
    os.rename(src, dst)

parser = argparse.ArgumentParser(description="Runner for scripts package")
parser.add_argument('--e', type=int, help="Executes exercise from --l by script number", choices=scripts_d.keys(), required=False)
parser.add_argument('--d', type=int, help="Displays exercise code from --l by script number", choices=scripts_d.keys(), required=False)
parser.add_argument('--l', type=str, help="Display all package scripts. Accepts path")
parser.add_argument('--s', type=str, help="Search for string in package files")
args = parser.parse_args()

if args.e is not None:
    script = scripts_d[int(args.e)]
    # script = re.sub("[ ,]", '_', script)
    print(script)
elif args.d is not None:
    script = scripts_d[int(args.d)]


if __name__ == '__main__':
    main(args.e, args.d, args.l, args.s)
