#! /usr/bin/env python
"""
This script will ask a series of questions of a script, and generate a
configuration dictionary to setup a django-integrator compliant project.

"""
import sys


SCRIPT = [
    ['', 
     'what kind of input I expect', 
     'what variable it is stored at'],
]

def call_centre(args, script=None):
    "This will go through the script"
    if script is None:
        script = SCRIPT

    print('#' * 79)
    position = 0
    while len(script) > position:
        row = script[position]
        text = row[0].strip()
        text += '\n'
        text += '#' * 79
        print(text)
        var = input('# ')
        position += 1



def main():
    args = sys.argv[::]
    call_centre(args)

if __name__ == '__main__':
    main()