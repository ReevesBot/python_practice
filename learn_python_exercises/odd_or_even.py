#!/usr/bin/python3

num = int(input("Please enter a number: "))
num2 = int(input("And a second one please: "))
##Check if the number is even or odd, and if it's divisable by four##
if num % 2 == 0 and num % 4 == 0:
	print("Rad! That first number's divisible by four!")
elif num % 2 == 0:
	print("That first one is hella even!")
else:
	print("Hmm.. that first one's odd...")

##Check to see if the two numbers are divisible by eachother##
if num % num2 == 0:
	print(str(num) + " is divisible by " + str(num2))
else:
	print(str(num) + " is not divisible by " + str(num2))

if num2 % num == 0:
	print(str(num2) + " is divisible by " + str(num))
else:
	print(str(num2) + " is not divisible by " + str(num))
