step_1_3_shell = """#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced

source activate maker_p

GENOME=$1
TAG=$2
tRNA_file=%s
CRL_DIR=%s

# 2.1.1. Collection of candidate elements with LTRs that are 99%% or more in similarity using LTRharvest
mkdir $TAG
cd $TAG

gt suffixerator -db $GENOME -indexname $TAG.index -tis -suf -lcp -des -ssp -dna
gt ltrharvest -index $TAG.index -out $TAG.out99 -outinner $TAG.outinner99 -gff3 $TAG.gff99 -minlenltr 100 -maxlenltr 6000 -mindistltr 1500 -maxdistltr 25000 -mintsd 5 -maxtsd 5 -motif tgca -similar 99 -vic 10  > $TAG.result99

# 2.1.2. Using LTRdigest to find elements with PPT (poly purine tract) or PBS (primer binding site)
gt gff3 -sort $TAG.gff99 > $TAG.gff99.sort
gt ltrdigest -trnas $tRNA_file $TAG.gff99.sort $TAG.index > $TAG.gff99.dgt

perl $CRL_DIR/CRL_Step1.pl --gff $TAG.gff99.dgt

# 2.1.3. Further filtering of the candidate elements
perl $CRL_DIR/CRL_Step2.pl --step1 CRL_Step1_Passed_Elements.txt --repeatfile $TAG.out99 --resultfile $TAG.result99 --sequencefile $GENOME --removed_repeats CRL_Step2_Passed_Elements.fasta

mkdir fasta_files
mv Repeat_*.fasta fasta_files
mv CRL_Step2_Passed_Elements.fasta fasta_files
cd fasta_files

perl $CRL_DIR/CRL_Step3.pl --directory ../fasta_files --step2 CRL_Step2_Passed_Elements.fasta --pidentity 60 --seq_c 25

mv  CRL_Step3_Passed_Elements.fasta  ..
cd  ..
        
"""

step_1_3_85_shell = """#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced
# 2.2. Collection of relatively old LTR retrotransposons

source activate maker_p

GENOME=$1
TAG=$2
tRNA_file=%s
CRL_DIR=%s

# 2.1.1
mkdir ${TAG}
cd ${TAG}

gt suffixerator -db $GENOME -indexname $TAG.index -tis -suf -lcp -des -ssp -dna
gt ltrharvest -index $TAG.index -out $TAG.out85 -outinner $TAG.outinner85 -gff3 $TAG.gff85 -minlenltr 100 -maxlenltr 6000 -mindistltr 1500 -maxdistltr 25000 -mintsd 5 -maxtsd 5 -vic 10  > $TAG.result85

# 2.1.2. Using LTRdigest to find elements with PPT (poly purine tract) or PBS (primer binding site)
gt gff3 -sort $TAG.gff85 > $TAG.gff85.sort
gt ltrdigest -trnas $tRNA_file $TAG.gff85.sort $TAG.index > $TAG.gff85.dgt

perl $CRL_DIR/CRL_Step1.pl --gff $TAG.gff85.dgt

# 2.1.3. Further filtering of the candidate elements
perl $CRL_DIR/CRL_Step2.pl --step1 CRL_Step1_Passed_Elements.txt --repeatfile $TAG.out85 --resultfile $TAG.result85 --sequencefile $GENOME --removed_repeats CRL_Step2_Passed_Elements.fasta

mkdir fasta_files
mv Repeat_*.fasta fasta_files
mv CRL_Step2_Passed_Elements.fasta fasta_files
cd fasta_files

perl $CRL_DIR/CRL_Step3.pl --directory ../fasta_files --step2 CRL_Step2_Passed_Elements.fasta --pidentity 60 --seq_c 25

mv  CRL_Step3_Passed_Elements.fasta  ..
cd  ..

"""

step_4_5_shell = """#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced

source activate maker_p

GENOME=%s
TAG=all
tRNA_file=%s
CRL_DIR=%s
MITE_file=%s
Tpase_dir=%s

# 2.1.4. Identify elements with nested insertions

perl $CRL_DIR/ltr_library.pl --resultfile $TAG.result99 --step3 $TAG.CRL_Step3_Passed_Elements.fasta --sequencefile $GENOME
cat lLTR_Only.lib $MITE_file  > repeats_to_mask_LTR99.fasta
RepeatMasker -pa 56 -lib repeats_to_mask_LTR99.fasta -nolow -dir . $TAG.outinner99
perl $CRL_DIR/cleanRM.pl $TAG.outinner99.out $TAG.outinner99.masked > $TAG.outinner99.unmasked
perl $CRL_DIR/rmshortinner.pl $TAG.outinner99.unmasked 50 > $TAG.outinner99.clean

blastx -query $TAG.outinner99.clean -db $Tpase_dir/Tpases020812DNA -evalue 1e-10 -num_descriptions 10 -out $TAG.outinner99.clean_blastx.out.txt -num_threads 56
perl $CRL_DIR/outinner_blastx_parse.pl --blastx $TAG.outinner99.clean_blastx.out.txt --outinner $TAG.outinner99

# 2.1.5 Building examplars

perl $CRL_DIR/CRL_Step4.pl --step3 $TAG.CRL_Step3_Passed_Elements.fasta --resultfile $TAG.result99 --innerfile passed_outinner_sequence.fasta --sequencefile $GENOME

makeblastdb -in lLTRs_Seq_For_BLAST.fasta -dbtype nucl
blastn -query lLTRs_Seq_For_BLAST.fasta -db lLTRs_Seq_For_BLAST.fasta -evalue 1e-10 -num_descriptions 1000 -out lLTRs_Seq_For_BLAST.fasta.out -num_threads 56

makeblastdb -in Inner_Seq_For_BLAST.fasta -dbtype nucl
blastn -query Inner_Seq_For_BLAST.fasta -db Inner_Seq_For_BLAST.fasta  -evalue 1e-10 -num_descriptions 1000 -out  Inner_Seq_For_BLAST.fasta.out -num_threads 56

perl $CRL_DIR/CRL_Step5.pl --LTR_blast lLTRs_Seq_For_BLAST.fasta.out --inner_blast Inner_Seq_For_BLAST.fasta.out --step3 $TAG.CRL_Step3_Passed_Elements.fasta --final LTR99.lib --pcoverage 90 --pidentity 80

"""


step_4_5_85_shell = """#! /bin/bash

# http://weatherby.genetics.utah.edu/MAKER/wiki/index.php/Repeat_Library_Construction-Advanced

source activate maker_p

GENOME=%s
TAG=all
tRNA_file=%s
CRL_DIR=%s
MITE_file=%s
Tpase_dir=%s

# 2.1.4. Identify elements with nested insertions

perl $CRL_DIR/ltr_library.pl --resultfile $TAG.result85 --step3 $TAG.CRL_Step3_Passed_Elements.fasta --sequencefile $GENOME
cat lLTR_Only.lib $MITE_file  > repeats_to_mask_LTR85.fasta
RepeatMasker -pa 56 -lib repeats_to_mask_LTR85.fasta -nolow -dir . $TAG.outinner85
perl $CRL_DIR/cleanRM.pl $TAG.outinner85.out $TAG.outinner85.masked > $TAG.outinner85.unmasked
perl $CRL_DIR/rmshortinner.pl $TAG.outinner85.unmasked 50 > $TAG.outinner85.clean

blastx -query $TAG.outinner85.clean -db $Tpase_dir/Tpases020812DNA -evalue 1e-10 -num_descriptions 10 -out $TAG.outinner85.clean_blastx.out.txt -num_threads 56
perl $CRL_DIR/outinner_blastx_parse.pl --blastx $TAG.outinner85.clean_blastx.out.txt --outinner $TAG.outinner85

# 2.1.5 Building examplars

perl $CRL_DIR/CRL_Step4.pl --step3 $TAG.CRL_Step3_Passed_Elements.fasta --resultfile $TAG.result85 --innerfile passed_outinner_sequence.fasta --sequencefile $GENOME

makeblastdb -in lLTRs_Seq_For_BLAST.fasta -dbtype nucl
blastn -query lLTRs_Seq_For_BLAST.fasta -db lLTRs_Seq_For_BLAST.fasta -evalue 1e-10 -num_descriptions 1000 -out lLTRs_Seq_For_BLAST.fasta.out -num_threads 56

makeblastdb -in Inner_Seq_For_BLAST.fasta -dbtype nucl
blastn -query Inner_Seq_For_BLAST.fasta -db Inner_Seq_For_BLAST.fasta  -evalue 1e-10 -num_descriptions 1000 -out  Inner_Seq_For_BLAST.fasta.out -num_threads 56

perl $CRL_DIR/CRL_Step5.pl --LTR_blast lLTRs_Seq_For_BLAST.fasta.out --inner_blast Inner_Seq_For_BLAST.fasta.out --step3 $TAG.CRL_Step3_Passed_Elements.fasta --final LTR85.lib --pcoverage 90 --pidentity 80

"""

MITE_shell = """source activate maker_p && \\
cp %s %s/genome.fasta && \\
perl %s -i genome.fasta -g %s -c %d -n %d -S 12345678 && \\
cat *Step8_* > MITE.lib
"""

merge85_99_shell = """source activate maker_p && \\
RepeatMasker -pa 56 -lib LTR99.lib -dir . LTR85.lib && \\
perl %s/remove_masked_sequence.pl --masked_elements LTR85.lib.masked --outfile FinalLTR85.lib && \\
cat LTR99.lib FinalLTR85.lib > allLTR.lib
"""

RepeatMasker_shell = """#! /bin/bash
    
source activate maker_p

GENOME=$1
TAG=$2
all_LIB=%s

mkdir ${TAG}
cd ${TAG}

RepeatMasker -lib $all_LIB -dir . $GENOME
"""

RepeatModeler_shell = """#! /bin/bash
CRL_DIR=%s
Tpase_dir=%s
            
source activate maker_p

cat */*.fa.masked > all.fa.masked
perl $CRL_DIR/rmaskedpart.pl all.fa.masked 50  >  all.fa.umseqfile
sed '/^$/d' all.fa.umseqfile > all.fa.fullline.umseqfile
BuildDatabase -name umseqfiledb -engine ncbi all.fa.fullline.umseqfile
RepeatModeler -pa 14 -database umseqfiledb

perl $CRL_DIR/repeatmodeler_parse.pl --fastafile RM*/consensi.fa.classified --unknowns repeatmodeler_unknowns.fasta --identities repeatmodeler_identities.fasta

# makeblastdb -in $Tpase_dir/Tpases020812  -dbtype prot
blastx -query repeatmodeler_unknowns.fasta -db $Tpase_dir/Tpases020812 -num_threads 56 -evalue 1e-10 -num_descriptions 10 -out modelerunknown_blast_results.txt
perl $CRL_DIR/transposon_blast_parse.pl --blastx modelerunknown_blast_results.txt --modelerunknown repeatmodeler_unknowns.fasta

mv  unknown_elements.txt  ModelerUnknown.lib
cat  identified_elements.txt  repeatmodeler_identities.fasta  > ModelerID.lib
"""

get_final_lib_shell = """#! /bin/bash
DIR_PE=%s

source activate maker_p

$DIR_PE/ProtExcluder.pl -f 50 ModelerUnknown.lib_blast_results.txt ModelerUnknown.lib
$DIR_PE/ProtExcluder.pl -f 50 MITE.lib_blast_results.txt MITE.lib
$DIR_PE/ProtExcluder.pl -f 50 ModelerID.lib_blast_results.txt ModelerID.lib

sed 's/(//g;s/)//g' allLTR.lib > allLTR.lib.re
sed 's/_(/_/g;s/)_/_/g' allLTR.lib_blast_results.txt > allLTR.lib_re_blast_results.txt

perl $DIR_PE/ProtExcluder.pl -f 50 allLTR.lib_re_blast_results.txt allLTR.lib.re
cat MITE.libnoProtFinal allLTR.lib.renoProtFinal ModelerID.libnoProtFinal > KnownRepeats.lib
cat KnownRepeats.lib ModelerUnknown.libnoProtFinal > allRepeats.lib
"""