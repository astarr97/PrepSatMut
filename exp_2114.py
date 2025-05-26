import sys

file = sys.argv[1]
contig_file = sys.argv[2]

o = open(contig_file)
d = {}
for line in o:
    l = line.replace("\n", "").split("\t")
    d[l[0]] = int(l[2])

assert(".bed" in file)

o = open(file)
out = open(file.replace(".bed", ".2114.bed"), 'w')

#Open file to flag those that we had to expand in odd ways
out2 = open(file.split("/")[0] + "/Flagged_Not_Originally_2114.txt", 'w')

for line in o:
    l = line.replace("\n", "").split("\t")
    
    #Compute how far off we are from 2114 bases
    dif = 2114 - (int(l[2]) - int(l[1]))
    
    #If it is even then it is easy, if it is odd we expand at the end by 1 base
    if abs(dif) % 2 == 0:
        new_start = str(int(int(l[1]) - dif//2))
        new_end = str(int(int(l[2]) + dif//2))
    else:
        new_start = str(int(int(l[1]) - dif//2))
        new_end = str(int(int(l[2]) + dif//2) + 1)
    
    flag = 0
    #If the proposed new_start and new_end are within the bounds of the chromosome, write out
    if int(new_start) >= 0 and int(new_end) < d[l[0]]:
        l[1] = new_start
        l[2] = new_end
        out.write("\t".join(l) + "\n")
    #If the beginning is negative and the end is beyond the end of the chrom, write out the maximum sequence length
    elif int(new_start) < 0 and int(new_end) >= d[l[0]]:
        l[1] = str(0)
        l[2] = str(d[l[0]] - 1)
        out.write("\t".join(l) + "\n")
        out2.write("\t".join(l + ["ContigTooShort"]) + "\n")
        flag = "ContigTooShort"
    #If only the start is negative, extend the end so we get 2114 bases
    elif int(new_start) < 0:
        l[1] = str(0)
        l[2] = str(min(int(new_end) - int(new_start), d[l[0]]))
        out.write("\t".join(l) + "\n")
        #print(int(l[2]) - int(l[1]))
        out2.write("\t".join(l + ["StartLessThan0"]) + "\n")
    #If only the end is beyond the length of the chromosome, extend it
    elif int(new_end) >= d[l[0]]:
        
        l[1] = str(max(0, int(new_start) - (int(new_end) - d[l[0]] + 1)))
        l[2] = str(d[l[0]] - 1)
        #print(int(l[2]) - int(l[1]))
        out2.write("\t".join(l + ["EndGreaterThanMax"]) + "\n")
        out.write("\t".join(l) + "\n")
    #Commented out effectively, use during testing
    if int(l[2]) - int(l[1]) != 2114:
        #print(int(l[2]) - int(l[1]), flag)
        #print(line)
        #print(l)
        pass
        
out.close()
o.close()
