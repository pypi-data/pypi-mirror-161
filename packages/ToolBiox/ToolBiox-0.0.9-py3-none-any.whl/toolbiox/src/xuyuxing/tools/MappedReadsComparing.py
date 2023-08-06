import pysam
from toolbiox.lib.common.genome.seq_base import read_fastq_big

def get_top_M_score(read_aln_list):
    top_M = 0
    
    for aln in read_aln_list:
        cigar_list = aln.cigar
        TM = sum([i[1] for i in cigar_list if i[0] == 0])
        DM = sum([i[1] for i in cigar_list if not (i[0] == 0 or i[0] == 3)])

        M = TM - DM

        if M > top_M:
            top_M = M
    
    return top_M


def get_best_alignment_match_number(read_aln_list):
    valid_aln_list = [alignedsegment for alignedsegment in read_aln_list if not (alignedsegment.is_secondary or alignedsegment.is_supplementary)]

    # get 1-end
    read1_aln_list = [alignedsegment for alignedsegment in valid_aln_list if alignedsegment.is_read1]

    # get 2-end
    read2_aln_list = [alignedsegment for alignedsegment in valid_aln_list if alignedsegment.is_read2]

    read1_top_M = get_top_M_score(read1_aln_list)
    read2_top_M = get_top_M_score(read2_aln_list)

    M_score = read1_top_M + read2_top_M

    return M_score

def get_tag(read_aln_list1, read_aln_list2, tag1, tag2):
    M1 = get_best_alignment_match_number(read_aln_list1)
    M2 = get_best_alignment_match_number(read_aln_list2)

    if M1 > M2:
        return tag1, M1, M2
    elif M2 > M1:
        return tag2, M1, M2
    else:
        return "X", M1, M2

def extract_aln_by_reads(reads_name, name_indexed):
    output_list = []
    try:
        name_indexed.find(reads_name)
    except KeyError:
        pass
    else:
        iterator = name_indexed.find(reads_name)
        output_list = []
        for x in iterator:
            output_list.append(x)
    
    return output_list

def index_bam_file(bam_file):
    bamfile = pysam.AlignmentFile(bam_file, 'rb')
    name_indexed = pysam.IndexedReads(bamfile)
    name_indexed.build()
    header = bamfile.header.copy()
    return name_indexed, header

def get_read_name_list_from_fastq(fastq_file_name, output_file_name):
   
    with open(output_file_name, 'w') as f:
        for record in read_fastq_big(fastq_file_name,gzip_flag=True):
            f.write(record[0].seqname_short() + "\n")

    return output_file_name

def MappedReadsComparing_main(args):
    reads_id_file= get_read_name_list_from_fastq(args.fastq_file, args.reads_id_file)


    # indexed the bam file
    name_indexed_1, header1 = index_bam_file(args.mapped_bam_file_1)
    name_indexed_2, header2 = index_bam_file(args.mapped_bam_file_2)

    # remove the None element
    with open(args.tag_file, 'w') as w:
        with open(args.reads_id_file, 'r') as f:
            for each_line in f:
                read_name = each_line.strip()
        
                # extracting the alignmentseqments
                read_aln_list_1= extract_aln_by_reads(read_name, name_indexed_1)
                read_aln_list_2= extract_aln_by_reads(read_name, name_indexed_2)
        
                tag, M1 , M2  = get_tag(read_aln_list_1, read_aln_list_2, args.tag1, args.tag2)

                w.write("%s\t%s\t%d\t%d\n" % (read_name, tag, M1, M2))