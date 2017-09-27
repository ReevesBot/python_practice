#!/usr/bin/python3

import datetime
from datetime import date

this_year = date.today().year
this_year = int(this_year)
print(this_year)
birthyear = input("What is your birthyear: ")
birthyear = int(birthyear)
current_age = int(this_year - birthyear)
print("If you were born in " + str(birthyear) + " then you must be " + str(current_age))
print("That means you will turn 100 in " + str(100 - current_age) + " years")
