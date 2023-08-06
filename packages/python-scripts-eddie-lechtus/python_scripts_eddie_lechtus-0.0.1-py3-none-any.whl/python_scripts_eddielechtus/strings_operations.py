import inspect
import re
import traceback

functions = ["get_last_character", "get_first_character", "get_middle_character", "get_all_after", "get_all_before", "get_beetwin_indexes",
             "concatinate", "removestring", "multiplytring", "replace", "endswith", "startwith", "find", "index", "isalnum", "isalpha",
             "isascii", "isdecimal", "isdigit", "isnumeric", "isidentifier", "isprintable", "isspace", "strip", "lstrip", "rfind", "rindex",
             "rsplit", "split", "swapcase", "title", "findall", "search", "regex_split", "sub"]


class Strings:
    def get_last_character(self, string):
        last = string[-1]
        return ("method: last = string[-1]", "res: ", last)


    def get_first_character(self, string):
        first = string[0]
        return ("method: first = string[0]", "res : ", first)


    def get_middle_character(self, string):
        print("string : ", string)
        middle_pos = int(len(self, string)) // 2
        middle = string[middle_pos]
        code = inspect.getsource(self.get_middle_character)
        return ("method: {} res: {} ".format(code, middle))


    def get_all_after(self, string):
        print("string : ", string)
        ui = input("Enter word from string\n")
        all_after = string.partition(ui)
        code = inspect.getsource(self.get_all_after)
        return ("method : {} res: {}".format(code, all_after[2]))


    def get_all_before(self, string):
        print("string : ", string)
        ui = input("Enter word from string\n")
        all_after = string.partition(ui)
        code = inspect.getsource(self.get_all_before)
        return ("method : {} res: {}".format(code, all_after[0]))


    def get_beetwin_indexes(self, string):
        print("string : ", string)
        idxstart = input("enter start index between %s\n" %len(string))
        idxtop = input("enter stop index between %s\n" %len(string))
        res = string[int(idxstart):int(idxtop)]
        code = inspect.getsource(self.get_beetwin_indexes)
        return("method : {} res : {} ".format(code, res))


    def concatinate(self, string):
        print("string : ", string)
        ui = input("input string to add\n")
        contr = string + ui
        code = inspect.getsource(self.concatinate)
        return ("method : {} res : {} ".format(code, contr))


    def removestring(self, string):
        print("string : ", string)
        ui = input("enter string to remove\n")
        rm = string.strip(ui)
        code = inspect.getsource(self.removestring)
        return ("method : {} res : {} ".format(code, rm))


    def multiplytring(self, string):
        print("string : ", string)
        ui = input("enter multiplication number\n")
        mul = string * int(ui)
        code = inspect.getsource(self.multiplytring)
        return ("method : {} res : {} ".format(code, mul))


    #build in methods
    def replace(self, string):
        print("string : ", string)
        rep = input("enter string to replace\n")
        newtr = input("enter new string\n")
        res = string.replace(rep, newtr)
        code = inspect.getsource(self.replace)
        return ("method : {} res : {} ".format(code, res))


    def endswith(self, string):
        print("string : ", string)
        ui = input("enter character to check\n")
        res = string.endswith(ui)
        code = inspect.getsource(self.endswith)
        return ("method : {} res : {} ".format(code, res))


    def startwith(self, string):
        print("string : ", string)
        ui = input("enter character to check\n")
        res = string.startswith(ui)
        code = inspect.getsource(self.startwith)
        return ("method : {} res : {} ".format(code, res))


    def find(self, string):  #same as index except: does not print Exception
        print("string : ", string)
        ui = input("enter character to check\n")
        res = string.find(ui)
        code = inspect.getsource(self.find)
        return ("method : {} res : {} ".format(code, res))


    def index(self, string):
        print("string : ", string)
        ui = input("enter character to check\n")
        res = string.index(ui)
        missing = input("try character what is not present\n")
        try:
             string.index(missing)
        except ValueError:
            traceback.print_exc()
        code = inspect.getsource(self.index)
        return ("method : {} res : {} ".format(code, res))



    def isalnum(self, string):
        print("string : ", string)
        res = string.isalnum()
        code = inspect.getsource(self.isalnum)
        return ("method : {} res : {} ".format(code, res))


    def isalpha(self, string):
        print("string : ", string)
        res = string.isalpha()
        code = inspect.getsource(self.isalpha)
        return ("method : {} res : {} ".format(code, res))


    def isascii(self, string):
        print("string : ", string)
        res = string.isalpha()
        code = inspect.getsource(self.isascii)
        return ("method : {} res : {} ".format(code, res))


    def isdecimal(self, string):
        print("string : ", string)
        res = string.isdecimal()
        code = inspect.getsource(self.isdecimal)
        return ("method : {} res : {} ".format(code, res))


    def isdigit(self, string):
        print("string : ", string)
        res = string.isdigit()
        code = inspect.getsource(self.isdigit)
        return ("method : {} res : {} ".format(code, res))


    def isnumeric(self, string):
        print("string : ", string)
        res = string.isnumeric()
        code = inspect.getsource(self.isnumeric)
        return ("method : {} res : {} ".format(code, res))


    def isidentifier(self, string):
        print("string : ", string)
        res = string.isidentifier()
        code = inspect.getsource(self.isidentifier)
        return ("method : {} res : {} ".format(code, res))


    def isprintable(self, string):
        print("string : ", string)
        res = string.isprintable()
        code = inspect.getsource(self.isprintable)
        return ("method : {} res : {} ".format(code, res))


    def isspace(self, string):
        print("string : ", string)
        res = string.isspace()
        code = inspect.getsource(self.isspace)
        return ("method : {} res : {} ".format(code, res))
    

    def lstrip(self, string):
        print("string : ", string)
        res = string.lstrip()
        code = inspect.getsource(self.lstrip)
        return ("method : {} res : {} ".format(code, res))


    def rfind(self, string):
        print("string : ", string)
        ui = input("enter string to find its last occurrence\n")
        res = string.rfind(ui)
        code = inspect.getsource(self.rfind)
        return ("method : {} res : {} ".format(code, res))


    def rindex(self, string):
        print("string : ", string)
        ui = input("enter string to find its last occurrence\n")
        res = string.rindex(ui)
        code = inspect.getsource(self.rindex)
        return ("method : {} res : {} ".format(code, res))


    def rsplit(self, string):
        print("string : ", string)
        ui = input("enter char to split\n")
        res = string.rsplit(ui)
        code = inspect.getsource(self.rsplit)
        return ("method : {} res : {} ".format(code, res))


    def split(self, string):
        print("string : ", string)
        ui = input("enter char to split\n")
        res = string.split(ui)
        code = inspect.getsource(self.split)
        return ("method : {} res : {} ".format(code, res))


    def strip(self, string):
        print("string : ", string)
        ui = input("enter string to strip\n")
        res = string.strip(ui)
        code = inspect.getsource(self.strip)
        return ("method : {} res : {} ".format(code, res))


    def swapcase(self, string):
        print("string : ", string)
        res = string.swapcase()
        code = inspect.getsource(self.swapcase)
        return ("method : {} res : {} ".format(code, res))


    def title(self, string):
        print("string : ", string)
        res = string.title()
        code = inspect.getsource(self.title)
        return ("method : {} res : {} ".format(code, res))


    #regex
    def findall(self, string):
        print("string : ", string)
        numbers = re.findall("[0-9]", string)
        print(numbers)
        ui = input("enter string to find all occurrences\n")
        res = re.findall(ui, string)
        code = inspect.getsource(self.findall)
        return ("method : {} res : {} ".format(code, res))

    def search(self, string):
        print("string : ", string)
        ui = input("enter string to first occurrence\n")
        res = re.search(ui, string)
        code = inspect.getsource(self.search)
        return ("method : {} res : {} ".format(code, res))


    def regex_split(self, string):
        print("string : ", string)
        print("split by spaces : '\s'\n")
        res = re.split('\s', string)
        code = inspect.getsource(self.regex_split)
        return ("method : {} res : {} ".format(code, res))


    def sub(self, string):
        print("string : ", string)
        ui = input("enter char to replace spaces\n")
        print("replace spaces by : %s" %ui)
        res = re.sub('\s', ui, string)
        code = inspect.getsource(self.sub)
        return ("method : {} res : {} ".format(code, res))


    def call_by_number(self, string, ui):
        func = functions_dict[int(ui)]          #same as functions_dict.get(ui)
        method = None
        method = getattr(obj, func)
        print(method(string))

    def call_by_name(self, string, ui):
        func = functions_dict.get(ui)
        method = None
        method = getattr(obj, func)
        print(method(string))


#Driver code
flag = True
res = None
res_k = None
obj = Strings()
keys = range(len(functions))
functions_dict = dict(zip(keys, functions))
for key, val in functions_dict.items():
    print(key, val)
print("************************************")
string = "    Endurance log: Greenock 16/06/22 16 degrees rain    0"

while flag:
    ui = input("choose function by number or type 'm' to search by name or 'n' by number. press 'q' to quit\n")
    if re.search("[0-9]", ui):
        obj.call_by_number(string, ui)

    match ui:
        case 'm':
            sf = input("enter method to search\n")
            res = [x for x in functions_dict.values() if x == sf]
            res = res[0]
            if res != None:
                values_list = list(functions_dict.values())
                key = values_list.index(res)
                ui = key
                obj.call_by_name(string, ui)

        case 'n':
            key_idx = input("enter number to search\n")
            obj.call_by_number(string, key_idx)

        case 'q':
            break




