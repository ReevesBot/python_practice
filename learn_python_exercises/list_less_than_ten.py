#!/usr/bin/python3

num_list = [1,2,3,4,5,6,7,8,9,10,12,14,16,18,20]
new_list = [ ]
usr_num = int(input("Please enter a number: "))

for i in num_list: 
	if i <= 10: 
		new_list.append(i)
print(new_list)

for i in new_list:
	if i <= usr_num:
		print(i)
