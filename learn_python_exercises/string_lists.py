#!/usr/bin/python3

usr_str = str(input("Please input a string: "))
new_usr_str = usr_str.replace(" ", "")
new_usr_str.lstrip()
new_usr_str.rstrip()
str_array = [ ]
reverse_array = [ ]

for i in new_usr_str:
	str_array.append(i)
	reverse_array.append(i)

reverse_array.reverse()

if str_array == reverse_array:
	print("That's a palindrome!")
else:
	print("That's not a palindrome")
