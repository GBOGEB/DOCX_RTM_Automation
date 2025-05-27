# Example code with lint issues
import os, sys  # Multiple imports on one line (PEP 8 violation)

def myFunction( ):  # Extra space before parentheses (PEP 8 violation)
    print( "Hello, World!" )  # Extra spaces inside parentheses (PEP 8 violation)
    print("This is a test")
    print("Another statement")  # Fixed missing newline

myFunction()
