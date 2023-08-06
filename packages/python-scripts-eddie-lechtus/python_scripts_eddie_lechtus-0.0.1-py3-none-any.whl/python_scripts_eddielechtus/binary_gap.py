# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")

def solution(N):
    flag = False
    zero_flag = False
    count = 0
    zero = 0
    biggest = 0
    binary_str = bin(N).replace("0b", "")
    print(binary_str)
    for c in binary_str:
        if c == '1':
            if zero_flag:
                count += 1
                if count == 1:
                    if zero > biggest:
                        biggest = zero
                        zero = 0
                        count = 0
                        flag = True
        else:
            zero_flag = True
            zero += 1


    if flag:
        return biggest
    else:
        return 0



# userInput = input("enter number\n")
# if int(userInput) > 0:
#     solution(int(userInput))
# else:
#     print("only positive number allowed")

print(solution(512))
print(solution(528))
print(solution(6))
print(solution(328))
print(solution(5))
print(solution(16))
print(solution(1024))
print(solution(51712))
print(solution(1))