import sys

file = sys.argv[1]
assert(".tsv" in file)

o = open(file)
out = open(file.replace(".tsv", ".bed"), 'w')

c = 0
for line in o:
    l = line.replace("\n", "").split("\t")
    if c and l[1] != "refPosition":
        #Convert to the 0-start bed format
        out.write("\t".join([l[0], l[1], str(int(l[1]) + 1)] + [x if x else "." for x in l[2:]]) + "\n")
    c += 1
o.close()
out.close()
