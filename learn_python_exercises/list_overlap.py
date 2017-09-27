#!/usr/bin/python3

import random

list_a = [ ]                   
list_b = [ ]
i = 0                   

while i < 11:
	list_a.append(random.randrange(20))
	list_b.append(random.randrange(20))
	i = i+1
print(list_a, list_b)

print(set(list_a) & set(list_b))
