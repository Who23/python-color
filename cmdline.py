import sys, tty, termios, code

old_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)
cursorIndex = 0
line = ""
i = code.InteractiveInterpreter()

with open("builtins.txt") as builtinstxt:
    builtins = [line.rstrip() for line in builtinstxt]

with open("keywords.txt") as keywordstxt:
    keywords = [line.rstrip() for line in keywordstxt]
    

def formatLine(line):
    line = line.split(" ")
    for index, word in enumerate(line):
        ending = ""
        for func in builtins:
            if func in word:
                temp = word.split(func)
                temp0 = len(temp[0])
                temp1 = len(temp[1])
                
                if ((not temp0) or temp[0][-1] in "([{}])") and ((not temp1) or temp[1][0] in "([{}])"):
                     line[index] = temp[0] + "\u001b[35m" + func + "\u001b[0m" + temp[1]
                    

        

        # if word in builtins:
        #     
        if word in keywords:
            if not ending:
                line[index] = "\u001b[33m" + word + "\u001b[0m"
        
    return ' '.join(line)


while True:
    try:
        typed = ord(sys.stdin.read(1))
        #print(typed)

        #check for special key presses
        #CTRL+C
        if typed == 3:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print()
            quit()
        #arrow keys
        elif typed == 27:
            _, typed = sys.stdin.read(2)

            #right arrow
            if ord(typed) == 67:
                cursorIndex += 1 if cursorIndex != len(line) else 0
            #left arrow
            elif ord(typed) == 68:
                cursorIndex -= 1 if cursorIndex != 0 else 0

        #backspace
        elif typed == 127:
            if cursorIndex != 0:
                line = line[:cursorIndex-1] + line[cursorIndex:]
                cursorIndex -= 1

        #tab
        elif typed == 9:
            line += "    "
            cursorIndex += 4
            

        #enter
        elif typed == 13:
            try:
                result = code.compile_command(line)
            except Exception as e:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                print(e)
                tty.setraw(sys.stdin)
                result = False
                line = ""
            finally:
                if result == None and result != False:
                    line += "\n"
                    print()
                else:
                    sys.stdout.write("\n\u001b[1000D")
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    i.runcode(result)
                    tty.setraw(sys.stdin)
                    line = ""
                    sys.stdout.write("\n\u001b[1B")
                cursorIndex = 0

        else:
            line += chr(typed)
            cursorIndex += 1

        formatted_line = formatLine(line)
        #write out to the terminal, moving cursor as well

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        newlinecount = line.count("\n")
        if newlinecount:
             sys.stdout.write(f"\u001b[K\u001b[{newlinecount}A")
        print("\u001b[1000D\u001b[K" + formatted_line, end="\r")
        if cursorIndex:
            sys.stdout.write(f"\u001b[1000D\u001b[{cursorIndex}C")
        sys.stdout.flush()
        tty.setraw(sys.stdin)

    #except any errors and quit nicely
    except Exception as e:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print(e)
        quit()

