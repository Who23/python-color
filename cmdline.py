import sys, tty, termios, code, os, re

old_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)
# column, row
cursorIndex = [0, 0]
prevLines = []
hasTyped = False
upArrowOnWhich = 0

line = ""
i = code.InteractiveInterpreter()

# get our builtins to highlight
with open(f'{os.path.dirname(os.path.abspath(__file__))}/builtins.txt') as builtinstxt:
    builtins = [line.rstrip() for line in builtinstxt]

# get our keywords to highlight
with open(f'{os.path.dirname(os.path.abspath(__file__))}/keywords.txt') as keywordstxt:
    keywords = [line.rstrip() for line in keywordstxt]
    

# regexes for highlighting
strreg = r'''((".+?")|(".+"?))|(('.+?')|('.+'?))'''
builtinsreg = r"\b(" + r''.join(f"({x})|" for x in builtins)[:-1] + r")\b"
keywordsreg = r"\b(" + r''.join(f"({x})|" for x in keywords)[:-1] + r")\b"
colorString = r'\u001b\[3(3|5)m.*?\u001b\[0m'

def formatLine(line):
    # highlight all keywords and builtins
    line = re.sub(builtinsreg, lambda match : "\u001b[35m" + match.group(0) + "\u001b[0m", line)
    line = re.sub(keywordsreg, lambda match : "\u001b[33m" + match.group(0) + "\u001b[0m", line)

    # highlight all strings green, and unhighlight any keyword or builtin in the string
    line = re.sub(strreg, 
        lambda match : "\u001b[32m" + 
        re.sub(colorString, lambda m : m.group(0).strip('\u001b[1234567890m'), match.group(0)) + \
        "\u001b[0m", line)

    # add the beginning '>>> ' or '... '
    line = line.split("\n")

    line[0] = ">>> " + line[0]
    for index, word in enumerate(line[1:]):
        line[index+1] = "... " + word
    line = '\n'.join(line)
        
    return line
    
    
# print python3 vesion and python-color commit
vi = sys.version_info
pcolorString = "\u001b[1m\u001b[31mc\u001b[33mo\u001b[32ml\u001b[34mo\u001b[35mr\u001b[0m"
sys.stdout.write(f"::: Python {vi[0]}.{vi[1]}.{vi[2]} || {pcolorString} #{sys.argv[1]} :::\u001b[0m\n\r")
sys.stdout.write(">>> ")
sys.stdout.flush()

while True:
    try:
        typed = ord(sys.stdin.read(1))

        # check for special key presses
        # CTRL+C
        if typed == 3:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print()
            quit()
        
        # arrow keys
        elif typed == 27:
            _, typed = sys.stdin.read(2)

            # up arrow
            if ord(typed) == 65:
                # if the user has not typed anything on the line they are on
                if not hasTyped:
                    # increase the command history ref index by 1
                    if upArrowOnWhich < len(prevLines):
                        upArrowOnWhich += 1

                        # modify that line to the line in the command history
                        a = line.split("\n")
                        a[cursorIndex[1]] = prevLines[-1*upArrowOnWhich]
                        cursorIndex[0] = len(prevLines[-1*upArrowOnWhich])
                        line = '\n'.join(a)

                else:
                    # move up the cursor unless we're at the top
                    # print(cursorIndex[1])
                    if cursorIndex[1] > 0:
                        cursorIndex[1] -= 1
                        sys.stdout.write("\u001b[1A")

            # down arrow
            elif ord(typed) == 66:
                # if we aren't in a new line and the user has not typed anything on the line they're on
                # print(hasTyped)
                if line.split("\n")[cursorIndex[1]] != "" and not hasTyped:
                    # decrease the command history ref index by 1
                    upArrowOnWhich -= 1 if upArrowOnWhich > 0 else 0

                    # if we aren't back at the fresh line
                    if upArrowOnWhich != 0:
                        # modify that line
                        a = line.split("\n")
                        a[cursorIndex[1]] = prevLines[-1*upArrowOnWhich]
                        line = '\n'.join(a)

                        # set the cursor index correctly
                        cursorIndex[0] = len(prevLines[-1*upArrowOnWhich])
                    else:
                        # if it is the fresh line, clear it out
                        line = ""
                        cursorIndex[0] = 0
                else:
                    # moves down the cursor if we aren't at the bottom
                    if cursorIndex[1] != line.count("\n"):
                        cursorIndex[1] += 1
                        sys.stdout.write("\u001b[1B")

            # right arrow
            elif ord(typed) == 67:
                cursorIndex[0] += 1 if cursorIndex[0] != len(line.split("\n")[cursorIndex[1]]) else 0
                hasTyped = True if cursorIndex[0] != len(line.split("\n")[cursorIndex[1]]) else False

            # left arrow
            elif ord(typed) == 68:
                cursorIndex[0] -= 1 if cursorIndex[0] != 0 else 0
                hasTyped = True

        # backspace
        elif typed == 127:
            if cursorIndex[0] != 0:
                # delete the character at the position of the cursor
                tempLine = line.split("\n")
                tempLine1 = tempLine[cursorIndex[1]]
                tempLine1 = tempLine1[:cursorIndex[0]-1] + tempLine1[cursorIndex[0]:]
                tempLine[cursorIndex[1]] = tempLine1
                line = "\n".join(tempLine)
                
                cursorIndex[0] -= 1
                hasTyped = True

        # tab
        elif typed == 9:
            line += "    "
            cursorIndex[0] += 4
            hasTyped = True
            
        # enter
        elif typed == 13:
            try:
                # compile the command
                result = code.compile_command(line)
            except Exception as e:
                # if there's an error in the command, it will throw an error
                # print it out and reset
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                print()
                print(e)
                tty.setraw(sys.stdin)

                # add line to command line history
                for miniLine in line.split("\n"):
                    if miniLine != "":
                        prevLines.append(miniLine)
                        
                result = False
                line = ""
            finally:
                if result == None and result != False:
                    # None means that the command isn't finished, and more input is needed
                    line += "\n"
                    cursorIndex[1] += 1
                    upArrowOnWhich = 0
                    print()
                else:
                    # if we're good, run the code
                    sys.stdout.write("\n\u001b[1000D")
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    i.runcode(result)
                    tty.setraw(sys.stdin)

                    # add line to command line history
                    for miniLine in line.split("\n"):
                        if miniLine != "":
                            prevLines.append(miniLine)

                    # reset stuff
                    line = ""
                    hasTyped = False
                    upArrowOnWhich = 0
                    cursorIndex[1] = 0
                cursorIndex[0] = 0

        # anything else
        else:
            tempLine = line.split("\n")
            # insert the typed character
            tempLine1 = tempLine[cursorIndex[1]]
            tempLine1 = tempLine1[:cursorIndex[0]] + chr(typed) + tempLine1[cursorIndex[0]:]
            tempLine[cursorIndex[1]] = tempLine1
            line = "\n".join(tempLine)
            hasTyped = True
            
            cursorIndex[0] += 1

        if line == "":
            # if we're on a new line, let the user use the command line history
            hasTyped = False



        formatted_line = formatLine(line)

        # # write out to the terminal, moving cursor as well ##
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        newlinecount = line.count("\n")

        # move the cursor to the bottom of the text
        for x in range(newlinecount - cursorIndex[1]):
            sys.stdout.write("\u001b[1B")
        

        # if we have newlines, write them out
        if newlinecount:
            # moves back to first line and cleans each line on the way
            for x in range(newlinecount):
                sys.stdout.write("\r\u001b[K\u001b[1A")


        # using print instead of sys.stdout.write b/c if @ the botton of the screen
        # it doesn't add a new line and messes everything up
        print("\u001b[1000D\u001b[K" + formatted_line + "\u001b[1000D\u001b[4C", end="")
            
        # move the cursors into their appropriate spots
        if cursorIndex[1] != newlinecount:
            upByHowMuch = newlinecount - cursorIndex[1]
            sys.stdout.write(f"\u001b[{upByHowMuch}A")
        if cursorIndex[0]:
            sys.stdout.write(f"\u001b[{cursorIndex[0]}C")
    

        sys.stdout.flush()
        tty.setraw(sys.stdin)

    # except any errors and quit nicely
    except Exception as e:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("\n\u001b[31mError in python-color!\u001b[0m")
        print(e)
        quit()