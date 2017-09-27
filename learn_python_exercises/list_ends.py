#!/usr/bin/python3

import random

##simple solution############################################
#def newList(userList):                                     #
#    revisedList = [ ]                                      #
#    revisedList.append(userList[0])                        #
#    revisedList.append(userList[6])                        #
#    return(revisedList)                                    #
#                                                           #
#userList = [ ]                                             #
#i = 0                                                      #
#while i < 7:                                               #
#    userList.append(int(input("Please enter a number: "))) #
#    i = i + 1                                              #
#                                                           #
#revisedList = newList(userList)                            #
#print(revisedList)                                         #
#############################################################

i = [ ]
print(list(i.append(random.sample(range(100), k=10)) or i[0:-1] for x in i))
