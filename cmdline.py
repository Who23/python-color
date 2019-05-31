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

#get our builtins to highlight
with open(f'{os.path.dirname(os.path.abspath(__file__))}/builtins.txt') as builtinstxt:
    builtins = [line.rstrip() for line in builtinstxt]

#get our keywords to highlight
with open(f'{os.path.dirname(os.path.abspath(__file__))}/keywords.txt') as keywordstxt:
    keywords = [line.rstrip() for line in keywordstxt]
    
# For future referece this function is broken down into 3 sections
# first, we take the line and split the regions seperated by '. This means that
# every other 'chunk' is a single quote string, which we format green
# if it's not a single quote string 'chunk', we split it further into regions seperated by ".
# this does the same thing - every other chunk is a string. For the non-string regions here,
# we finally format them accordingly by seperating them by spaces and looking for keywords and 
# builtins to color.
def formatLine(line):
    #actually format it with color!
    line = line.split("'")
    for overIndex, doubleline in enumerate(line):
        if overIndex % 2 == 0:
            doubleline = doubleline.split('"')
            for index, lineChunk in enumerate(doubleline):
                if index % 2 == 0:
                    #if we are in a non-string 'chunk'
                    lineChunk = lineChunk.split(" ")
                    for chunkIndex, word in enumerate(lineChunk):
                        for func in builtins:
                            if func in word:
                                #if we find the function in the word, split the sentence into before and after
                                #the function
                                temp = word.split(func)
                                temp0 = len(temp[0])
                                temp1 = len(temp[1])
                                
                                #If we have chars before/after the function and they're parentheses, color code the function
                                if ((not temp0) or temp[0][-1] in "([{}])") and ((not temp1) or temp[1][0] in "([{}])"):
                                    lineChunk[chunkIndex] = temp[0] + "\u001b[35m" + func + "\u001b[0m" + temp[1]
                                    
                        # highlights keywords in orange
                        if word in keywords:
                            lineChunk[chunkIndex] = "\u001b[33m" + word + "\u001b[0m"
                    lineChunk = " ".join(lineChunk)
                else:
                    #color the string section green!
                    lineChunk = "\u001b[32m" + lineChunk + "\u001b[0m"

                doubleline[index] = lineChunk

            doubleline = '"'.join(doubleline)
        else:
            doubleline = "\u001b[32m" + doubleline + "\u001b[0m"
        line[overIndex] = doubleline

    #re-join the line and add the beginning '>>> ' or '... '
    line = "'".join(line).split("\n")

    line[0] = ">>> " + line[0]
    for index, word in enumerate(line[1:]):
        line[index+1] = "... " + word
    line = '\n'.join(line)
        
    return line

sys.stdout.write(">>> ")
sys.stdout.flush()
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

            #up arrow
            if ord(typed) == 65:
                #if the user has not typed anything on the line they are on
                if not hasTyped:
                    #increase the command history ref index by 1
                    if upArrowOnWhich < len(prevLines):
                        upArrowOnWhich += 1

                        #modify that line to the line in the command history
                        a = line.split("\n")
                        a[cursorIndex[1]] = prevLines[-1*upArrowOnWhich]
                        line = '\n'.join(a)

                        #set the cursor index correctly
                        cursorIndex[0] = len(prevLines[-1*upArrowOnWhich])
                else:
                    #move up the cursor unless we're at the top
                    #print(cursorIndex[1])
                    if cursorIndex[1] > 0:
                        cursorIndex[1] -= 1
                        sys.stdout.write("\u001b[1A")

            #down arrow
            elif ord(typed) == 66:
                #if we aren't in a new line and the user has not typed anything on the line they're on
                #print(hasTyped)
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
                else:
                    #moves down the cursor if we aren't at the bottom
                    if cursorIndex[1] != line.count("\n"):
                        cursorIndex[1] += 1
                        sys.stdout.write("\u001b[1B")

            #right arrow
            elif ord(typed) == 67:
                cursorIndex[0] += 1 if cursorIndex[0] != len(line) else 0
            #left arrow
            elif ord(typed) == 68:
                cursorIndex[0] -= 1 if cursorIndex[0] != 0 else 0

        #backspace
        elif typed == 127:
            if cursorIndex[0] != 0:
                #delete the character at the position of the cursor
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
                #compile the command
                result = code.compile_command(line)
            except Exception as e:
                #if there's an error in the command, it will throw an error
                #print it out and reset
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                print()
                print(e)
                tty.setraw(sys.stdin)
                result = False
                line = ""
            finally:
                if result == None and result != False:
                    #None means that the command isn't finished, and more input is needed
                    line += "\n"
                    cursorIndex[1] += 1
                    upArrowOnWhich = 0
                    print()
                else:
                    #if we're good, run the code
                    sys.stdout.write("\n\u001b[1000D")
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    i.runcode(result)
                    tty.setraw(sys.stdin)

                    #add line to command line history
                    for miniLine in line.split("\n"):
                        if miniLine != "":
                            prevLines.append(miniLine)

                    #reset stuff
                    line = ""
                    hasTyped = False
                    upArrowOnWhich = 0
                    cursorIndex[1] = 0
                cursorIndex[0] = 0

        #anything else
        else:
            tempLine = line.split("\n")
            #insert the typed character
            tempLine1 = tempLine[cursorIndex[1]]
            tempLine1 = tempLine1[:cursorIndex[0]] + chr(typed) + tempLine1[cursorIndex[0]:]
            tempLine[cursorIndex[1]] = tempLine1
            line = "\n".join(tempLine)
            hasTyped = True
            
            cursorIndex[0] += 1

        if line == "":
            #if we're on a new line, let the user use the command line history
            hasTyped = False

        formatted_line = formatLine(line)

        #write out to the terminal, moving cursor as well
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        newlinecount = line.count("\n")

        #move the cursor to the bottom of the text
        for x in range(newlinecount - cursorIndex[1]):
            sys.stdout.write("\u001b[1B")
        

        #if we have newlines, write them out
        if newlinecount:
            #moves back to first line and cleans each line on the way
            for x in range(newlinecount):
                sys.stdout.write(f"\r\u001b[K\u001b[1A")


        #using print instead of sys.stdout.write b/c if @ the botton of the screen
        #it doesn't add a new line and messes everything up
        print("\u001b[1000D\u001b[K" + formatted_line, end="")
            
        #move the cursors into their appropriate spots
        if cursorIndex[0]:
            sys.stdout.write(f"\u001b[1000D\u001b[{cursorIndex[0]+4}C")
        if cursorIndex[1] != newlinecount:
            upByHowMuch = newlinecount - cursorIndex[1]
            sys.stdout.write(f"\u001b[{upByHowMuch}A")
    

        sys.stdout.flush()
        tty.setraw(sys.stdin)

    #except any errors and quit nicely
    except Exception as e:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("\n\u001b[31mError in python-color!\u001b[0m")
        print(e)
        quit()