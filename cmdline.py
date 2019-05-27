#TODO: Make single quote strings formatted
#TODO: Add up and down arrow navigation
#TODO: Add more comments

import sys, tty, termios, code, os

old_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)
#column, row
cursorIndex = [0, 0]
prevLines = []
hasTyped = False
upArrowOnWhich = 0

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

        #check for special key presses
        #CTRL+C
        if typed == 3:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print()
            quit()
        
        #arrow keys
        elif typed == 27:
            _, typed = sys.stdin.read(2)
            if ord(typed) == 65:
                #up arrow

                #if the user has not typed anything on the line they are on
                if not hasTyped:
                    #increase the command history ref index by 1
                    upArrowOnWhich += 1 if upArrowOnWhich < len(prevLines) else 0

                    #modify that line to the line in the command history
                    a = line.split("\n")
                    a[cursorIndex[1]] = prevLines[-1*upArrowOnWhich]
                    line = '\n'.join(a)

                    #set the cursor index correctly
                    cursorIndex[0] = len(prevLines[-1*upArrowOnWhich])
            elif ord(typed) == 66:
                #down arrow

                #if we aren't in a new line and the user has not typed anything on the line they're on
                if line.split("\n")[cursorIndex[1]] != "" and not hasTyped:
                    #decrease the command history ref index by 1
                    upArrowOnWhich -= 1 if upArrowOnWhich > 0 else 0

                    #if we aren't back at the fresh line
                    if upArrowOnWhich != 0:
                        #modify that line
                        a = line.split("\n")
                        a[cursorIndex[1]] = prevLines[-1*upArrowOnWhich]
                        line = '\n'.join(a)

                        #set the cursor index correctly
                        cursorIndex[0] = len(prevLines[-1*upArrowOnWhich])
                    else:
                        #if it is the fresh line, clear it out
                        line = ""
                        cursorIndex[0] = 0
            #right arrow
            elif ord(typed) == 67:
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
            hasTyped = True
            
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
                    upArrowOnWhich = 0
                    print()
                else:
                    sys.stdout.write("\n\u001b[1000D")
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    i.runcode(result)
                    tty.setraw(sys.stdin)
                    for miniLine in line.split("\n"):
                       prevLines.append(miniLine)
                    line = ""
                    hasTyped = False
                    upArrowOnWhich = 0
                    cursorIndex[1] = 0
                cursorIndex[0] = 0

        #anything else
        else:
            tempLine = line.split("\n")
            tempLine1 = tempLine[cursorIndex[1]]
            tempLine1 = tempLine1[:cursorIndex[0]] + chr(typed) + tempLine1[cursorIndex[0]:]
            tempLine[cursorIndex[1]] = tempLine1
            line = "\n".join(tempLine)
            
            cursorIndex[0] += 1

        if line == "":
            hasTyped = False

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

