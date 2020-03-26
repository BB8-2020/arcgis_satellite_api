import sys

if len(sys.argv) <= 1:
    exit()


__import__(sys.argv[1])


