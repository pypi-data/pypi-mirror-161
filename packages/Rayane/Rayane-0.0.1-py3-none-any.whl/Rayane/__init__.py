from collections import deque
import sys

filename = sys.argv[1]
file = open(f"{filename}.ryn", 'r')
contents = file.read()

q = deque()

i = 0
j = i
while (i < len(contents)):
    if (contents[i] == "\""):
        j += 1
    elif (contents[j] != "\""):
        i += 1
        if (contents[i] == ";"):
            print(q[0])