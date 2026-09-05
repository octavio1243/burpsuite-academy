# python read.py 4b463a3c35c96d8a70b5c5ce970105ab6d3db6
import sys, zlib

with open(sys.argv[1], "rb") as f:
    data = zlib.decompress(f.read())

print(data)
