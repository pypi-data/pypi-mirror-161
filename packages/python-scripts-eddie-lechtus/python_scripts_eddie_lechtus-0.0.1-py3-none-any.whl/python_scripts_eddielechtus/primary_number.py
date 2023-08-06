def primary(nums):
    # for n in nums:
    #     if int(n) % 2 > 0:
    #         print(n)
    res = [n for n in nums if int(n) % 2 > 0]
    return res


ui = input("enter numbers\n")
ui = ui.split(' ')
print(primary(ui))