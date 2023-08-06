def palindrom(ui):
    rev = ui
    rev[::-1]
    if ui == rev:
        return True
    else:
        return False

ui = input("enter number")
print(palindrom(ui))