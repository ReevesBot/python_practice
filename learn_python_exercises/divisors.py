#!/usr/bin/python3

user_num = int(input("Please input a number to be divided: "))
dividers = range(2, user_num)
results = [ ]

for i in dividers:
	if user_num % i == 0:
		results.append(i)
print(str(user_num) + " is divisble by " + str(results))
