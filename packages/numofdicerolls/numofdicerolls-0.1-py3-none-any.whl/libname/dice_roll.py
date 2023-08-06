#!/usr/bin/python
import random

def rolldice():
    while True:
        try:
            num_rolls = int(input("How many rolls of the dice do you want?: "))
        except NameError:
            print("Please enter a correct number")
            continue
        else:
            break

    for i in range(num_rolls):
        print(random.randint(1,6)+random.randint(1,6))
