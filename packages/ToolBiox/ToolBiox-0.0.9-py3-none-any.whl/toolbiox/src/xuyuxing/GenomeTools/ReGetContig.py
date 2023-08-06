from pyfaidx import Fasta
from toolbiox.lib.common.math.interval import merge_intervals
from toolbiox.lib.common.os import multiprocess_running
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from BCBio import GFF

def contig_range(SeqRecord_input):
    sequence = str(SeqRecord_input.seq)

    num = 1
    n_site = []
    for i in sequence:
        if i != "N":
            n_site.append((num, num))
        num = num + 1
    contig_range_output = merge_intervals(n_site, True)

    SeqRecord_input.features = []

    num = 0
    for contig_range_tmp in contig_range_output:
        qualifiers = {
            "source": "ReGetContig",
            "ID": "%s_%d" % (SeqRecord_input.id, num)
        }
        top_feature = SeqFeature(FeatureLocation(contig_range_tmp[0] - 1, contig_range_tmp[1]),
                                    type="contig", qualifiers=qualifiers)
        SeqRecord_input.features.append(top_feature)
        num = num + 1

    return SeqRecord_input


def ReGetContig_main(args):

    scaff_dir = Fasta(args.scaff_file)

    SeqRecord_list = []

    for scaff in scaff_dir:
        scaff_seq = Seq(str(scaff))
        SeqRecord_tmp = SeqRecord(scaff_seq, scaff.name)
        SeqRecord_list.append((SeqRecord_tmp,))

    cmd_result = multiprocess_running(
        contig_range, SeqRecord_list, args.threads, True)

    with open(args.output_gff3, 'w') as f:
        for i in cmd_result:
            GFF.write([cmd_result[i]['output']], f)

    with open(args.output_fasta, 'w') as f:
        for i in cmd_result:
            SeqRecord_tmp = cmd_result[i]['output']

            record_feature = SeqRecord_tmp.features
            for contig_feature in record_feature:
                start = int(contig_feature.location.start)
                end = int(contig_feature.location.end)
                ID = contig_feature.qualifiers['ID'][0]
                contig_seq = SeqRecord_tmp.seq[start:end]

                contig_record = SeqRecord(contig_seq, id=ID,
                                            description="%s:%d-%d" % (SeqRecord_tmp.id, start + 1, end))
                f.write(contig_record.format("fasta"))
                # SeqIO.write([contig_record], args.output_fasta, "fasta")

if __name__ == "__main__":
    class abc():
        pass

    args=abc()

    args.scaff_file = "/lustre/home/xuyuxing/Database/Cuscuta/Csp/Csp.fa"
    args.threads = 5
    args.output_gff3 = "/lustre/home/xuyuxing/Work/Csp/HiC/contig.gff3"
    args.output_fasta = "/lustre/home/xuyuxing/Work/Csp/HiC/contig.fasta"

    ReGetContig_main(args)
