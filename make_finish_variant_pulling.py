import pandas as pd
import os
import sys
import numpy as np

prog_rep = sys.argv[1]

v = pd.read_csv(prog_rep, skiprows = 3, sep = "\t")

for index, row in v.iterrows():
    if row["ApproxProportionDone"] == 1:
        files = os.listdir(row["Folder"])
        for f in files:
            if ".Variants.sort.bed" in f:
                o = open(folder + "/" + f)
                c = 0
                for line in o:
                    c+=1
                o.close()
                if c > 500000:
                    print("Variants file exists and has " + str(c) + " lines, suggesting all is completed for " + folder)
                else:
                    print("Variants file exists and has " + str(c) + " lines, suggesting it may not have completed for " + folder)
            else:
                print("Variants file does not exist, suggesting incompletion for " + folder)
    else:
        species = row["Folder"]
        last_seen = row["LastChrom"]
        all_chroms = row["AllChroms"].split("\t")
        NODE = species
        
        file = species + ".children.txt"
        o = open("SatMut/Children/" + file)
        for line in o:
            if line != "\n":
                CHILDREN = line.replace("\n", "").replace(" ", ",")
        o.close()

        all_chroms = list(np.setdiff1d(all_chroms, [last_seen]))
        v2 = pd.read_csv(species + "/" + species + "_contigs.bed", sep = "\t", header = None)
        v2 = v2[~v2[0].isin(all_chroms)]
        out = open("finish_vars_" + species + ".sh", 'w')
        time="168"
        MEM="16GB"
        
        focal = "Homo_sapiens"
        
        region_file = "ORTHOSPECIES/AllPrim_Regions_Summits.FOCALSPECIES.ORTHOSPECIES.Min500.Max3000.ProtDist200.bed".replace("FOCALSPECIES", focal).replace("ORTHOSPECIES", species)

        region_file = region_file.replace(".bed", ".2114.bed")

        out.write("#!/bin/bash\n#SBATCH --time=" + time + ":00:00\n#SBATCH -p hbfraser\n#SBATCH --mem=" + MEM + "\n#SBATCH -c 1\n\n")
        out.write('cactus_path="/scratch/users/astarr97/Common_Software/cactus-bin-v2.6.13/bin/"\n')
        out.write('hal_path="/scratch/users/astarr97/PhyloP/hg38.447way.hal"\n\n')
        for i in v2[0]:
            out.write("${cactus_path}halSnps --noDupes --minSpeciesForSnp 1 --refSequence " + i +" --tsv ORTHOSPECIES/ORTHOSPECIES_CHILDRENDOT.".replace("ORTHOSPECIES", species).replace("CHILDRENDOT", CHILDREN.replace(",", ".")) + i + ".PC.tsv $hal_path ORTHOSPECIES CHILDREN\n".replace("ORTHOSPECIES", species).replace("CHILDREN", CHILDREN))
        out.write("cat " + species + "/*.tsv > " + "ORTHOSPECIES/ORTHOSPECIES_CHILDRENDOT.allsnps.".replace("ORTHOSPECIES", species).replace("CHILDRENDOT", CHILDREN.replace(",", ".")) + "catted" + ".tsv\n")
        out.write("python convert_tsv_to_bed.py ORTHOSPECIES/TSV_OUT".replace("ORTHOSPECIES", species).replace("TSV_OUT", NODE + "_" + CHILDREN.replace(",", ".") + ".allsnps.catted.tsv") + "\n")
        snp_file = "ORTHOSPECIES/BED_OUT".replace("ORTHOSPECIES", species).replace("BED_OUT", NODE + "_" + CHILDREN.replace(",", ".")) + ".allsnps.catted.bed"
        out.write("sort -u " + snp_file + " | sort -k1,1 -k2,2n > " + snp_file.replace(".bed", ".sort.bed") + "\n")
        out.write("bedtools intersect -sorted -g ORTHOSPECIES/ORTHOSPECIES_contigs.sort.txt -wao -a ".replace("ORTHOSPECIES", species) + region_file.replace(".bed", ".sort.bed") + " -b " + snp_file.replace(".bed", ".sort.bed") + " > " + region_file.replace(".bed", ".Variants.sort.bed").replace(".Min500.Max3000.ProtDist200", "_" + CHILDREN.replace(",", ".")) + "\n")
        out.write("rm " + species + "/*.PC.tsv\n")

        out.close()