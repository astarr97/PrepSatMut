### IMPORTANT NOTE ###
#If this is the first time you are running the pipeline on a new hal file, you will need to run the following to get the necessary info (nodes and parent-child relationships) needed for the pipeline
mkdir Children
/scratch/users/astarr97/Common_Software/cactus-bin-v2.6.13/bin/halStats /scratch/users/astarr97/PhyloP/hg38.447way.hal > All_Branches.txt
python get_child_list.py
chmod 777 Get_Children.sh
./Get_Children.sh

#The goal of this pipeline is to, for a set of putative CREs:
#1. Pull all orthologous CREs for all primate (and tree shrew) nodes and leaves
#2. Get all variants for each ancestral node relative to its children
#3. Get fasta files for the sequences of the orthologous CREs

#To do this, we run make_lift_prim.py to generate a bunch of .sh files, one for each node in the primate tree
#These files hard code the path to cactus and the path to the hal file

#FOR ALL NODES
#The first step is to liftover the CREs and summits and then use halper (which should be installed in the same directory as make_lift_prim.py) to identify all the orthologous CREs we can
#Next, we pull the fasta file for that node and process it to produce files that will help later

#FOR ALL NODES
#We need the summit of this CRE (for deep learning we just pick the middle base) in a separate file called PREFIX.Summit.bed
#It is important to stick to this naming convention

#ONLY FOR ANCESTRAL NODES
#Only for ancestral nodes, we use halSNPs to pull all the SNPs for the two child nodes relative to the ancestral node
#We use a python script to convert that to a bed file then intersect with the list of orthologous CREs

#IMPORTANT
#Variant pulling probably won't finish for a lot of nodes, I am not sure why it is so slow
#You can run the following to check progress
#python check_progress.py to check how much of each has finished, see the notes in the output file for more details
#For some nodes, enough will get done that you can run:

#python make_finish_variant_pulling.py ProgressReport.txt
#This will create scripts that pull all variants for undone chromosomes and then cats things together and finishes things
#However, there is a limit on the size of a shell script you can submit as a job and if that limit is reached you can't run the job
#One potential workaround is to not run chromosomes less than 200 bases in length or something

#Output files
#With standard parameters, you will get files for all runs ending in:
#Min500.Max3000.ProtDist200.2114.sort.bed, which contains the orthologous regions expanded to 2114 bases in halper's output format
#Min500.Max3000.ProtDist200.bed, which contains the original halper output of orthologous regions
#Sequences.sort.fasta.bed, which contains the same information as the expanded orthologous regions file with the last column containing the sequence for that region in the specified genome

#For ancestral nodes, you'll also get
#A .tsv or catted.tsv file (depending on whether you had to do make_finish_variant_pulling.py) containing the full list of variants that were pulled
#Alternatively, you can save the equivalent .bed version
#These are in the standard halSNPs output format and the order of the species/ancestral nodes is contained in the name of the file
#.Variants.sort.bed, the result of intersecting the variants pulled with the expanded halper output, the columns are the halper output + the tsv output
