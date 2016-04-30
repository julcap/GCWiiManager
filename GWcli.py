# Library for CLI functions
import os
import sys

# Validate user input [y/n]
def validateYN(message):
    a=''
    while True:
        a = input(message + "[y/n]: ").lower()
        if a == "y" or a == "yes":
            return 1
        elif a == "n" or a == "no":
            return 0
        elif a == "e" or a == "exit":
            sys.exit(0)
        else:
            print("""Not a valid option, type "e" or "exit" to quit.""")
        
# Get game path from user input
def getGamesPath():
    path=''
    while not os.path.exists(path):
        path = input("Enter games location: ")
        if not os.path.exists(path):
            print("ERROR: {} not found.".format(path))
    return path

# Get destination folder
def getDestPath():
    while True:
        path = input("Enter destination folder: ")
        if os.path.exists(path):
            return path
        else:
            a = validateYN("The destination folder does not exist. Would you like to create it?")
            if a:
                os.mkdir(path)
                return path
