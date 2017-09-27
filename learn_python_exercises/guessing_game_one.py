#!/usr/bin/python3

import random

guess = int(0)
generate = int(0)
stop = False

def keepPlaying(playAgain):
    playAgain = input("Would you like to play again?(Y/N) ")
    playAgain = playAgain.upper()
    while True:
        if playAgain != "Y" and playAgain != "N":
            print("Please enter Y or N")
            playAgain = input("Would you like to play again?(Y/N) ")
            playAgain = playAgain.upper()
            continue
        else:
            return(playAgain)

while True:
    if generate == 0:
        ranNum = random.randrange(1, 10, 1)
        generate = 1

    if stop == True:
        break

    userNum = input("Please try to guess the number(1-9): ")

    if userNum == "exit":
        break

    try:
        userNum = int(userNum)

    except ValueError:
        print("Please enter a valid number")
        continue

    if userNum == ranNum:
        guess = guess + 1
        print("Good job, that's the right number. It took you " + str(guess) + " geusses!")
        playAgain = ()
        playAgain = keepPlaying(playAgain)
        if playAgain == "Y":
            guess = 0
            generate = 0
        else:
            stop = True

    elif userNum < ranNum:
        print("That's too low, try again!")
        guess = guess + 1

    elif userNum > ranNum:
        print("That's too high, try again!")
        guess = guess + 1
