def valid(parentheses):
    opener = '({['
    closer = ')}]'
    stack = []
    for c in parentheses:
        if c in opener:
            stack.append(c)
        else:
            if not stack:
                return False
            last = stack.pop()
            if closer[opener.index(last)] != c:
                return False
    if stack:
        return False

    return True


ui = input("enter parentheses\n")
print(valid(ui))