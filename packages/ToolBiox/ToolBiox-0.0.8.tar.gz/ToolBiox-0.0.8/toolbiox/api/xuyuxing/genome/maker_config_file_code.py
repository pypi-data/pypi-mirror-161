maker_config_string = """
#-----Genome (these are always required)
genome=%s #genome sequence (fasta file or fasta embeded in GFF3 file)
organism_type=eukaryotic #eukaryotic or prokaryotic. Default is eukaryotic


#-----Re-annotation Using MAKER Derived GFF3
maker_gff= #MAKER derived GFF3 file
est_pass=0 #use ESTs in maker_gff: 1 = yes, 0 = no
altest_pass=0 #use alternate organism ESTs in maker_gff: 1 = yes, 0 = no
protein_pass=0 #use protein alignments in maker_gff: 1 = yes, 0 = no
rm_pass=0 #use repeats in maker_gff: 1 = yes, 0 = no
model_pass=0 #use gene models in maker_gff: 1 = yes, 0 = no
pred_pass=0 #use ab-initio predictions in maker_gff: 1 = yes, 0 = no
other_pass=0 #passthrough anyything else in maker_gff: 1 = yes, 0 = no


#-----EST Evidence (for best results provide a file for at least one)
est=%s #set of ESTs or assembled mRNA-seq in fasta format
altest=%s #EST/cDNA sequence file in fasta format from an alternate organism
est_gff=%s #aligned ESTs or mRNA-seq from an external GFF3 file
altest_gff=%s #aligned ESTs from a closly relate species in GFF3 format


#-----Protein Homology Evidence (for best results provide a file for at least one)
protein=%s #protein sequence file in fasta format (i.e. from mutiple oransisms)
protein_gff=%s #aligned protein homology evidence from an external GFF3 file


#-----Repeat Masking (leave values blank to skip repeat masking)
model_org=all #select a model organism for RepBase masking in RepeatMasker
rmlib=%s #provide an organism specific repeat library in fasta format for RepeatMasker
repeat_protein=%s #provide a fasta file of transposable element proteins for RepeatRunner
rm_gff=%s #pre-identified repeat elements from an external GFF3 file
prok_rm=0 #forces MAKER to repeatmask prokaryotes (no reason to change this), 1 = yes, 0 = no
softmask=1 #use soft-masking rather than hard-masking in BLAST (i.e. seg and dust filtering)


#-----Gene Prediction
snaphmm=%s #SNAP HMM file
gmhmm= #GeneMark HMM file
augustus_species=%s #Augustus gene prediction species model
fgenesh_par_file= #FGENESH parameter file
pred_gff= #ab-initio predictions from an external GFF3 file
model_gff= #annotated gene models from an external GFF3 file (annotation pass-through)
est2genome=%d #infer gene predictions directly from ESTs, 1 = yes, 0 = no
protein2genome=%d #infer predictions from protein homology, 1 = yes, 0 = no
trna=1 #find tRNAs with tRNAscan, 1 = yes, 0 = no
snoscan_rrna=%s #rRNA file to have Snoscan find snoRNAs
unmask=0 #also run ab-initio prediction programs on unmasked sequence, 1 = yes, 0 = no


#-----Other Annotation Feature Types (features MAKER doesn't recognize)
other_gff= #extra features to pass-through to final MAKER generated GFF3 file


#-----External Application Behavior Options
alt_peptide=C #amino acid used to replace non-standard amino acids in BLAST databases
cpus=1 #max number of cpus to use in BLAST and RepeatMasker (not for MPI, leave 1 when using MPI)


#-----MAKER Behavior Options
max_dna_len=100000 #length for dividing up contigs into chunks (increases/decreases memory usage)
min_contig=1 #skip genome contigs below this length (under 10kb are often useless)


pred_flank=200 #flank for extending evidence clusters sent to gene predictors
pred_stats=0 #report AED and QI statistics for all predictions as well as models
AED_threshold=1 #Maximum Annotation Edit Distance allowed (bound by 0 and 1)
min_protein=0 #require at least this many amino acids in predicted proteins
alt_splice=0 #Take extra steps to try and find alternative splicing, 1 = yes, 0 = no
always_complete=0 #extra steps to force start and stop codons, 1 = yes, 0 = no
map_forward=0 #map names and attributes forward from old GFF3 genes, 1 = yes, 0 = no
keep_preds=0 #Concordance threshold to add unsupported gene prediction (bound by 0 and 1)


split_hit=10000 #length for the splitting of hits (expected max intron size for evidence alignments)
single_exon=0 #consider single exon EST evidence when generating annotations, 1 = yes, 0 = no
single_length=250 #min length required for single exon ESTs if 'single_exon is enabled'
correct_est_fusion=0 #limits use of ESTs in annotation to avoid fusion genes


tries=2 #number of times to try a contig if there is a failure for some reason
clean_try=0 #remove all data from previous run before retrying, 1 = yes, 0 = no
clean_up=0 #removes theVoid directory with individual analysis files, 1 = yes, 0 = no
TMP=%s #specify a directory other than the system default temporary directory for temporary files

"""


def write_maker_config(config_file, **kwargs):
    defaults_parameter = {
        "genome": "",
        "est": "",
        "altest": "",
        "est_gff": "",
        "altest_gff": "",
        "protein": "",
        "protein_gff": "",
        "rmlib": "",
        "repeat_protein": "",
        "rm_gff": "",
        "snaphmm": "",
        "augustus_species": "",
        "est2genome": 0,
        "protein2genome": 0,
        "snoscan_rrna": "",
        "TMP": "",
    }

    for k in kwargs:
        if k in defaults_parameter:
            defaults_parameter[k] = kwargs[k]

    parameter_tuple = (
        defaults_parameter["genome"],
        defaults_parameter["est"],
        defaults_parameter["altest"],
        defaults_parameter["est_gff"],
        defaults_parameter["altest_gff"],
        defaults_parameter["protein"],
        defaults_parameter["protein_gff"],
        defaults_parameter["rmlib"],
        defaults_parameter["repeat_protein"],
        defaults_parameter["rm_gff"],
        defaults_parameter["snaphmm"],
        defaults_parameter["augustus_species"],
        defaults_parameter["est2genome"],
        defaults_parameter["protein2genome"],
        defaults_parameter["snoscan_rrna"],
        defaults_parameter["TMP"],
    )

    with open(config_file, 'w') as f:
        f.write(maker_config_string % parameter_tuple)


maker_evaluate_anno_shell = """#! /bin/bash

source activate maker_p

index_log=%s

fasta_merge -d $index_log
gff3_merge -d $index_log
gff3_merge -n -s -d $index_log > genome.noseq.gff
grep -P "\\tgene\\t" genome.all.gff |grep "noncoding" -v|awk '{ sum += ($5 - $4) } END { print NR, sum / NR }' > gene.length
perl ~/Program/bin_xyx/AED_cdf_generator.pl -b 0.025 genome.all.gff  > AED.stat

conda deactivate

source activate busco4

busco -c 56 -m proteins -i genome.all.maker.proteins.fasta -o proteins_vs_embryophyta_odb10 -l embryophyta_odb10
rm -rf busco_downloads

conda deactivate
"""

def write_maker_evaluate_anno_shell(shell_file, index_log_file):
    with open(shell_file, 'w') as f:
        f.write(maker_evaluate_anno_shell % index_log_file)


maker_to_snap_augustus_shell = """#! /bin/bash

tag=$1
master_datastore_index_log=$2

source activate maker_p

# pae_r1
# Pae.frag.1_master_datastore_index.log


#############snap#################


# export 'confident' gene models from MAKER and rename to something meaningful
maker2zff -x 0.25 -l 50 -d $master_datastore_index_log 
# 20 min
file_prefix=${tag}.zff.length50_aed0.25
rename genome $file_prefix *


# gather some stats and validate
fathom $file_prefix.ann $file_prefix.dna -gene-stats > gene-stats.log 2>&1    
# 3 min
fathom $file_prefix.ann $file_prefix.dna -validate > validate.log 2>&1    
# 3 min


# collect the training sequences and annotations, plus 1000 surrounding bp for training
fathom $file_prefix.ann $file_prefix.dna -categorize 1000 > categorize.log 2>&1    
# 3 min
fathom uni.ann uni.dna -export 1000 -plus > uni-plus.log 2>&1    
# 1 min


# create the training parameters
mkdir params
cd params
forge ../export.ann ../export.dna > ../forge.log 2>&1    
# 1 min
cd ..


# assembly the HMM
hmm-assembler.pl $file_prefix params > $file_prefix.hmm    
# 1min


#############augustus#################

perl ~/Program/bin_xyx/zff2augustus_gbk.pl export.ann export.dna > augustus.gbk
new_species.pl --species=$tag
randomSplit.pl augustus.gbk 100
etraining --species=$tag augustus.gbk.train


# test
# augustus --species=$tag augustus.gbk.test | tee firsttest.out


# 迭代
export OMP_NUM_THREADS=1
optimize_augustus.pl --cpus=56 --kfold=56 --species=$tag augustus.gbk.train    
# 29 h

"""

def write_maker_to_snap_augustus_shell(shell_file):
    with open(shell_file, 'w') as f:
        f.write(maker_to_snap_augustus_shell)



inherit_maker_gff_shell = """#! /bin/bash
# transcript alignments
awk '{ if ($2 == "est2genome") print $0 }' genome.noseq.gff > for_next.est2genome.gff
# protein alignments
awk '{ if ($2 == "protein2genome") print $0 }' genome.noseq.gff > for_next.protein2genome.gff
# repeat alignments
awk '{ if ($2 ~ "repeat") print $0 }' genome.noseq.gff > for_next.repeats.gff
"""

def write_inherit_maker_gff_shell(shell_file):
    with open(shell_file, 'w') as f:
        f.write(inherit_maker_gff_shell)
