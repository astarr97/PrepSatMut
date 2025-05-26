import os
import pandas as pd
import numpy as np

out = open("ProgressReport.txt", 'w')
out.write("#Progress report for variant pulling\n")
out.write("#You can use this in conjunction with make_finish_variant_pulling.py to write scripts to finish variant pulling\n")
out.write("#This is an overestimate of the proportion done as it assumes the last chromosome seen is completely done, but this is never the case unless it is 100% done in which case it might be\n")
out.write("Folder\tApproxBasesDone\tTotalBases\tApproxProportionDone\tLastChrom\tAllChroms\n")

cc = 0
for folder in os.listdir():
    if folder.startswith("Primate") or folder.startswith("full") and "." not in folder:
        cc += 1
        v = pd.read_csv(folder + "/" + folder + "_contigs.bed", sep = "\t", header = None)
        f = 0
        for file in os.listdir(folder):
            if ".tsv" in file:
                f = file
        seen = []
        o = open(folder + "/" + f)
        c = 0
        
        for line in o:
            l = line.split("\t")
            seen.append(l[0])
            c += 1
            if c % 100000 == 0:
                seen = list(set(seen))
            last = l[0]
        o.close()
        seen = list(set(seen))
        tot = np.sum(v[2])
        done = np.sum(v[v[0].isin(seen)][2])
        out.write("\t".join([str(x) for x in [folder, done, tot, done/tot, last, ",".join(seen)]]) + "\n")
        print("\t".join([str(x) for x in [folder, done, tot, done/tot, last]]))

out.close()
