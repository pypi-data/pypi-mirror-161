#!/usr/bin/python

##########################################################################################
##           Script to calculate 4-fold degenerate transversion rate                    ##
##           © 2014 Pascal Pucholt pascal.pucholt@slu.se                                ##
##########################################################################################


from Bio.Data.CodonTable import unambiguous_dna_by_id
from Bio.Seq import Seq
from Bio import AlignIO
from math import log
import argparse

parser = argparse.ArgumentParser(description='Calculate 4DTV')
parser.add_argument('-f', '--file', dest='file', default="1.aln",
                    help='filename of fasta alignment file')
parser.add_argument('-t', '--tab', action="store_const", dest='tab', const=1, default=0,
                    help='Output in one tab separted line')

args = parser.parse_args()


def altcodons(codon, table):
    """
    list codons that code for the same aminoacid / are also stop
    @param codon
    @table code table id
    @return list of codons
    """

    tab = unambiguous_dna_by_id[table]

    if codon in tab.stop_codons:
        return tab.stop_codons

    try:
        aa = tab.forward_table[codon]
    except:
        return []

    return [k for (k, v) in tab.forward_table.iteritems() if v == aa and k[0] == codon[0] and k[1] == codon[1]]


def degeneration(codon, table):
    """
    determine how many codons code for the same amino acid / are also stop
    as codon

    @param codon the codon
    @param table code table id
    @param the number of codons also coding for the aminoacid codon codes for
    """

    return len(altcodons(codon, table))


def isXdegenerated(x, codon, table):
    """
    determine if codon is x-fold degenerated

    @param codon the codon
    @param table code table id
    @param true if x <= the degeneration of the codon
    """

    return (x <= len(altcodons(codon, table)))


def degenerated_subseq(seq, x, table):
    """
    get a subsequence consisting of the x-fold degenerated codons only
    """

    data = ""
    for i in range(0, len(seq), 3):
        codon = seq[i:i + 3].tostring()
        if isXdegenerated(x, codon, table):
            data += codon
    return data


alignment = AlignIO.read(open(args.file), "fasta")
FD = alignment[:, 0:0]
FDx = FD
ID = 0
TS = 0
TV = 0
for i in xrange(0, alignment.get_alignment_length(), 3):
    al2 = alignment[:, i:(i + 3)]
    if (isXdegenerated(4, al2[0].seq.tostring(), 1)):
        if (al2[0, 0:2].seq.tostring() == al2[1, 0:2].seq.tostring()):
            FD = FD + al2

for i in xrange(0, FD.get_alignment_length(), 3):
    al2 = FD[:, i:(i + 3)]
    site = al2[:, 2:3]
    FDx = FDx + site
    n1 = site[0].seq.tostring()
    n2 = site[1].seq.tostring()
    if (n1 == n2):
        ID = ID + 1
    elif ((n1 == "A" or n1 == "G") and (n2 == "A" or n2 == "G")):
        TS = TS + 1
    elif ((n1 == "C" or n1 == "T") and (n2 == "C" or n2 == "T")):
        TS = TS + 1
    else:
        TV = TV + 1

LO = (float)(FD.get_alignment_length() / 3)
FDTV = TV / LO
FDTS = TS / LO
FDS = (TS + TV) / LO
if FDTV < 0.5:
    FDTVC = -0.5 * log(1 - 2 * FDTV)
else:
    FDTVC = 99.0
LO = int(LO)

if args.tab:
    print
    LO, "\t", ID, "\t", TS, "\t", TV, "\t", FDS, "\t", FDTS, "\t", FDTV, "\t", FDTVC
else:
    print
    "# of 4D sites: ", LO
    print
    "# identical sites: ", ID
    print
    "# ts sites: ", TS
    print
    "# tv sites: ", TV
    print
    "4DTV:", FDTV
    print
    "4DTS:", FDTS
    print
    "4DS:", FDS
    if FDS < 0.5:
        print
        "4DTVc:", FDTVC

    # print FDx
