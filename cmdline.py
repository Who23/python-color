import sys, tty, termios, code, os

old_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)
#column, row
cursorIndex = [0, 0]
line = ""
i = code.InteractiveInterpreter()

with open(f'{os.path.dirname(os.path.abspath(__file__))}/builtins.txt') as builtinstxt:
    builtins = [line.rstrip() for line in builtinstxt]

with open(f'{os.path.dirname(os.path.abspath(__file__))}/keywords.txt') as keywordstxt:
    keywords = [line.rstrip() for line in keywordstxt]
    

def formatLine(line):
    #actually format it with color!
    line = line.split('"')
    for index, lineChunk in enumerate(line):
        if index % 2 == 0:
            lineChunk = lineChunk.split(" ")
            for chunkIndex, word in enumerate(lineChunk):
                for func in builtins:
                    if func in word:
                        temp = word.split(func)
                        temp0 = len(temp[0])
                        temp1 = len(temp[1])
                        
                        #make sure functions are being color coded properly, even if surrounded by 
                        #any parentheses
                        if ((not temp0) or temp[0][-1] in "([{}])") and ((not temp1) or temp[1][0] in "([{}])"):
                            lineChunk[chunkIndex] = temp[0] + "\u001b[35m" + func + "\u001b[0m" + temp[1]
                            
                # if word in builtins:
                if word in keywords:
                    lineChunk[chunkIndex] = "\u001b[33m" + word + "\u001b[0m"
            lineChunk = " ".join(lineChunk)
        else:
            lineChunk = "\u001b[32m" + lineChunk + "\u001b[0m"

        line[index] = lineChunk

    line = '"'.join(line).split("\n")
    line[0] = ">>> " + line[0]
    for index, word in enumerate(line[1:]):
        line[index+1] = "... " + word
    line = '\n'.join(line)
        
    return line


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
                cursorIndex[0] += 1 if cursorIndex[0] != len(line) else 0
            #left arrow
            elif ord(typed) == 68:
                cursorIndex[0] -= 1 if cursorIndex[0] != 0 else 0

        #backspace
        elif typed == 127:
            if cursorIndex[0] != 0:
                tempLine = line.split("\n")
                tempLine1 = tempLine[cursorIndex[1]]
                tempLine1 = tempLine1[:cursorIndex[0]-1] + tempLine1[cursorIndex[0]:]
                tempLine[cursorIndex[1]] = tempLine1
                line = "\n".join(tempLine)
                
                cursorIndex[0] -= 1

        #tab
        elif typed == 9:
            line += "    "
            cursorIndex[0] += 4
            

        #enter
        elif typed == 13:
            try:
                result = code.compile_command(line)
            except Exception as e:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                print()
                print(e)
                tty.setraw(sys.stdin)
                result = False
                line = ""
            finally:
                if result == None and result != False:
                    line += "\n"
                    cursorIndex[1] += 1
                    print()
                else:
                    sys.stdout.write("\n\u001b[1000D")
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    i.runcode(result)
                    tty.setraw(sys.stdin)
                    line = ""
                    sys.stdout.write("\n\u001b[1B")
                    cursorIndex[1] = 0
                cursorIndex[0] = 0

        else:
            line += chr(typed)
            cursorIndex[0] += 1

        formatted_line = formatLine(line)
        #write out to the terminal, moving cursor as well

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        newlinecount = line.count("\n")
        if newlinecount:
            #moves back to first line and cleans each line on the way
            for x in range(newlinecount):
                sys.stdout.write(f"\r\u001b[K\u001b[1A")

        #using print instead of sys.stdout.write b/c if @ the botton of the screen
        #it doesn't add a new line and messes everything up
        print("\u001b[1000D\u001b[K" + formatted_line, end="")
        if cursorIndex[0]:
            sys.stdout.write(f"\u001b[1000D\u001b[{cursorIndex[0]+4}C")
        sys.stdout.flush()
        tty.setraw(sys.stdin)

    #except any errors and quit nicely
    except Exception as e:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print(e)
        quit()

