#!/usr/bin/python3

def primeCheck():
    userNum = int(input("Please enter a number to be checked for primality: "))
    dividers = range(2, userNum)
    for i in dividers:
        if userNum % i == 0:
            return(True)

number = primeCheck()
if number == True:
    print("That number is not primal")

else:
    print("That is a primal number")
