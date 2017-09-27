#!/usr/bin/python3

import random

word_file = "/usr/share/dict/words"

def getWord():
    words = open(word_file).read().splitlines()
    randWord = random.choice(words)
    return(randWord)

def replacer(i):
    if i == 'a':
        coin = random.randint(1,7)
        if coin == 1:
            return("/\\")
        elif coin == 2:
            return("4")
        elif coin == 3:
            return("/-\\")
        elif coin == 4:
            return("/_\\")
        elif coin == 5:
            return("a")
        elif coin == 6:
            return("A")
        else:
            return("@")
    if i == 'e':
        return("3")
    if i == 'h':
        return("|-|")
    if i == 'l':
        return("1")
    if i == 'k':
        return("|<")
    if i == "m":
        return("/\/\\")
    if i == 'n':
        return("|\|")
    if i == 'o':
        return("0")
    if i == 's':
        return("5")
    if i == 't':
        return("+")
    if i == 'v':
        return("\/")
    if i == 'w':
        return("\/\/")
    if i == '\'':
        return("")
    else:
        coin = random.randint(1, 2)
        if coin == 1:
            i = i.capitalize()
        return(i)

while True:
    word = getWord()
    sWord = str(word)
    if (len(sWord)) <= 10:
        continue
    word = list(sWord)
    passwd = []
    for i in word:
       passwd.append(replacer(i))
    break


print("Your password is: ")
for i in passwd:
    print(i, end='')
print()
