import os

#Command to lift over the summits
command1 = "/scratch/users/astarr97/Common_Software/cactus-bin-v2.6.13/bin/halLiftover --bedType 3 /scratch/users/astarr97/PhyloP/hg38.447way.hal FOCALSPECIES AllPrim_Regions_Summits.bed ORTHOSPECIES ORTHOSPECIES/AllPrim_Regions_Summits.ORTHOSPECIES.bed\n"
#Command to liftover the regions
command2 = "/scratch/users/astarr97/Common_Software/cactus-bin-v2.6.13/bin/halLiftover --bedType 3 /scratch/users/astarr97/PhyloP/hg38.447way.hal FOCALSPECIES AllPrim_Regions.bed ORTHOSPECIES ORTHOSPECIES/AllPrim_Regions.ORTHOSPECIES.bed\n"

#Command to do halper
command3 = "python halLiftover-postprocessing/orthologFind.py -max_len 3000 -min_len 500 -protect_dist 200 -qFile AllPrim_Regions.bed -tFile ORTHOSPECIES/AllPrim_Regions.ORTHOSPECIES.bed -sFile ORTHOSPECIES/AllPrim_Regions_Summits.ORTHOSPECIES.bed -oFile ORTHOSPECIES/AllPrim_Regions_Summits.FOCALSPECIES.ORTHOSPECIES.Min500.Max3000.ProtDist200.bed -mult_keepone\n"
#Not used
command4 = "cd ORTHOSPECIES\npython ../postprocess_halper.py Adult_Kidney__ProximalTubule__Tiles_FOCALSPECIES.ORTHOSPECIES.Min500.Max3000.ProtDist200.bed\n"

species_all = ["fullTreeAnc114"]

#Iterate through and for any ancestral primate nodes (or near the primates) pull the children and the ancestral node
for file in os.listdir("SatMut/Children"):
    if "Prima" in file or file == "fullTreeAnc114.children.txt" or file == "fullTreeAnc113.children.txt" or file == "fullTreeAnc112.children.txt":
        o = open("SatMut/Children/" + file)
        for line in o:
            l = line.replace("\n", "").split(" ")
            species_all = species_all + l
            
#Command to pull the SNPs
command_snps = "${cactus_path}halSnps --noDupes --minSpeciesForSnp 1 --tsv ORTHOSPECIES/TSV_OUT $hal_path NODE CHILDREN\n"

for species in species_all:
    focal = "Homo_sapiens"
    #Create out file if it isn't done
    out_file = "lift_" + focal + "_" + species + ".sh"
    if out_file not in os.listdir("Done"):
        
        out = open(out_file, 'w')
        if species.startswith("full") or "000" in species:
            MEM = "64GB"
        else:
            MEM = "32GB"
        if species.startswith("full") or species.startswith("Primate"):
            time = "168"
        else:
            time = "72"
            
        #Write out the header
        out.write("#!/bin/bash\n#SBATCH --time=" + time + ":00:00\n#SBATCH -p hbfraser\n#SBATCH --mem=" + MEM + "\n#SBATCH -c 1\n\nmkdir ORTHOSPECIES\n".replace("ORTHOSPECIES", species))
        
        #Write out the path to cactus and the hal file, can change if needed
        out.write('cactus_path="/scratch/users/astarr97/Common_Software/cactus-bin-v2.6.13/bin/"\n')
        out.write('hal_path="/scratch/users/astarr97/PhyloP/hg38.447way.hal"\n\n')
        try:
            os.mkdir(focal)
        except:
            pass
        
        #Write out the initial commands
        out.write(command1.replace("FOCALSPECIES", focal).replace("ORTHOSPECIES", species))
        out.write(command2.replace("FOCALSPECIES", focal).replace("ORTHOSPECIES", species))
        out.write(command3.replace("FOCALSPECIES", focal).replace("ORTHOSPECIES", species))
        
        #Write out commands to create a fasta from the hal file and get chromosome sizes as well as genome file for bedtools
        out.write("\n#Make fasta\n")
        out.write("${cactus_path}hal2fasta --outFaPath ORTHOSPECIES/FASTA_OUT $hal_path ORTHOSPECIES\n".replace("ORTHOSPECIES", species).replace("FASTA_OUT", species + ".fasta"))
        out.write("samtools faidx ORTHOSPECIES/FASTA_OUT\n".replace("ORTHOSPECIES", species).replace("FASTA_OUT", species + ".fasta"))
        out.write("awk 'BEGIN {FS=" + '"\\t"' + "}; {print $1 FS " + '"0"' + " FS $2}' ORTHOSPECIES/ORTHOSPECIES.fasta.fai | sort -n -r -k 3,3 > ORTHOSPECIES/ORTHOSPECIES_contigs.bed\n".replace("ORTHOSPECIES", species))
        out.write("cut -f 1,3 ORTHOSPECIES/ORTHOSPECIES_contigs.bed > ORTHOSPECIES/ORTHOSPECIES_contigs.txt\n".replace("ORTHOSPECIES", species))
        out.write("sort -k1,1 -k2,2n ORTHOSPECIES/ORTHOSPECIES_contigs.txt > ORTHOSPECIES/ORTHOSPECIES_contigs.sort.txt\n".replace("ORTHOSPECIES", species))
        out.write("\n")
        
        #Write out commands to expand the regions created by halper, sort, and then get sequences for each region
        out.write("\n#Now getting fasta stuff\n")
        region_file = "ORTHOSPECIES/AllPrim_Regions_Summits.FOCALSPECIES.ORTHOSPECIES.Min500.Max3000.ProtDist200.bed".replace("FOCALSPECIES", focal).replace("ORTHOSPECIES", species)
        out.write("python exp_2114.py " + region_file + " " + species + "/" + species + "_contigs.bed\n")
        region_file = region_file.replace(".bed", ".2114.bed")
        out.write("sort -k1,1 -k2,2n " + region_file + " > " + region_file.replace(".bed", ".sort.bed") + "\n")
        out.write("bedtools getfasta -bedOut -name -fi ORTHOSPECIES/FASTA_OUT -bed ".replace("ORTHOSPECIES", species).replace("FASTA_OUT", species + ".fasta") + region_file.replace(".bed", ".sort.bed") + " > " + region_file.replace(".bed", ".Sequences.sort.fasta.bed\n"))
        
        #If it is an ancestral node we also need to pull variants
        #Note this will not finish for many ancestral nodes if you have a lot running at once, in that case you will need to restart things
        #TBD how to handle this because of limits on job submission file size
        if "Tree" in species and species.startswith("full") or species.startswith("Primate"):
            #Get the children
            out.write("\nNow getting variants stuff\n")
            file = species + ".children.txt"
            o = open("SatMut/Children/" + file)
            for line in o:
                if line != "\n":
                    CHILDREN = line.replace("\n", "").replace(" ", ",")
            o.close()
            NODE = file.split(".")[0]
            
            #Write out commands to get the SNPs
            out.write(command_snps.replace("ORTHOSPECIES", species).replace("NODE", NODE).replace("CHILDREN", CHILDREN).replace("TSV_OUT", NODE + "_" + CHILDREN.replace(",", ".") + ".allsnps.tsv"))
            
            #Write out command to convert to a bed file
            out.write("python convert_tsv_to_bed.py ORTHOSPECIES/TSV_OUT".replace("ORTHOSPECIES", species).replace("TSV_OUT", NODE + "_" + CHILDREN.replace(",", ".") + ".allsnps.tsv") + "\n")
        
        
        if "Tree" in species and species.startswith("full") or species.startswith("Primate"):
            snp_file = "ORTHOSPECIES/BED_OUT".replace("ORTHOSPECIES", species).replace("BED_OUT", NODE + "_" + CHILDREN.replace(",", ".")) + ".allsnps.bed"
            
            #Sort the snp file
            out.write("sort -k1,1 -k2,2n " + snp_file + " > " + snp_file.replace(".bed", ".sort.bed") + "\n")
            
            #Intersect with the expanded regions
            out.write("bedtools intersect -sorted -g ORTHOSPECIES/ORTHOSPECIES_contigs.sort.txt -wao -a ".replace("ORTHOSPECIES", species) + region_file.replace(".bed", ".sort.bed") + " -b " + snp_file.replace(".bed", ".sort.bed") + " > " + region_file.replace(".bed", ".Variants.sort.bed").replace(".Min500.Max3000.ProtDist200", "_" + CHILDREN.replace(",", ".")) + "\n")
    else:
        print(out_file)