import csv
import re
from sys import argv, exit

if len(argv) != 3:
    print("missing command_line argument")
    exit(1)
people = []
header = []

with open(argv[2],"r") as dna_file:
    DNA = dna_file.read()##<<<<<<<< TXT


## making list of headers to check with it
with open(argv[1],"r") as str_csv:
    CSV = csv.DictReader(str_csv)
    for row in CSV:
        header= row
        break
header = dict(list(header.items())[1:])


# make dict for the CSV to change the counts in it after counting
with open(argv[1],"r") as str_csv:
    CSV = csv.DictReader(str_csv)
    for row in CSV:
        people.append(row)
# count the longest headers

for i in range(len(header)):
    keys = list(header.keys())[i]
    Value = list(header.values())[i]
    count = 0
    countv = 0
    for j in range(len(DNA)):
        while count > 0:
            count-=1
            continue
        k = len(keys)
        if keys == DNA[j:k+j]:
            while DNA[j:k+j] == DNA[j-k:j]:
                count+=1
            if count > countv:
                countv = count
    print(countv)





