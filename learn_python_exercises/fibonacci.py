#!/usr/bin/python3

def fibonacci(steps):
    a = int(0)
    b = int(1)
    switch = True
    currentStep = 0
    sequence= [ ]

    while currentStep < steps:
        if switch == True:
            a = a + b
            currentStep = currentStep + 1
            switch = False
            sequence.append(a)

        else:
            b = b + a
            currentStep = currentStep + 1
            switch = True
            sequence.append(b)

    print("This is the fibonacci sequence out to the " + str(steps) + " digit" + str(sequence))

steps = int(input("How many digits would you like to know? "))
fibonacci(steps)
