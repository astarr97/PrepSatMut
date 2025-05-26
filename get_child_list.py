import sys

command = "/scratch/users/astarr97/Common_Software/cactus-bin-v2.6.13/bin/halStats --children NODE /scratch/users/astarr97/PhyloP/hg38.447way.hal > Children/NODE.children.txt\n"
out = open("Get_Children.sh", 'w')
o = open("All_Branches.txt")

for line in o:
    l = line.split(", ")
    if "Anc" in l[0] and "(" not in l[0]:
        out.write(command.replace("NODE", l[0]))
out.close()
o.close()
