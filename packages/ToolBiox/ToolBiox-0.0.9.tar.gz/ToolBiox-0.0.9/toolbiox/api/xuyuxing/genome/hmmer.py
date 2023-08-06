import re


class HmmTarget(object):
    """
    q : query
    t : target
    fs : fill sequence
    d : this domain
    hc : hmm coord
    ac : ali coord
    ec : env corrd
    """

    def __init__(self, name=None, accession=None, len=None, fs_evalue=None, fs_score=None, fs_bias=None,
                 description=None, HmmDomain_list=[]):
        self.name = name
        self.accession = accession
        self.description = description
        self.len = int(len)
        self.fs_evalue = float(fs_evalue)
        self.fs_score = float(fs_score)
        self.fs_bias = float(fs_bias)
        self.HmmDomain_list = HmmDomain_list

    def __str__(self):
        return "HmmTarget: %s. Len: %d, have %d HmmDomins\n" % (self.name, self.len, len(self.HmmDomain))


class HmmDomain(object):
    """
    q : query
    t : target
    fs : fill sequence
    d : this domain
    hc : hmm coord
    ac : ali coord
    ec : env corrd
    """

    def __str__(self):
        return "HmmDomins %s, found in %s, %d / %d\n" % (self.q_name, self.target.name, self.d_rank, self.d_total_num)

    def __init__(self, target, q_name=None, q_accesstion=None, q_len=None, d_rank=None, d_total_num=None,
                 d_cevalue=None, d_ievalue=None, d_score=None, d_bias=None, hc_from=None, hc_to=None, ac_from=None,
                 ac_to=None, ec_from=None, ec_to=None, acc=None):
        self.target = target
        self.q_name = q_name
        self.q_accesstion = q_accesstion
        self.q_len = int(q_len)
        self.d_rank = int(d_rank)
        self.d_total_num = int(d_total_num)
        self.d_cevalue = float(d_cevalue)
        self.d_ievalue = float(d_ievalue)
        self.d_score = float(d_score)
        self.d_bias = float(d_bias)
        self.hc_from = int(hc_from)
        self.hc_to = int(hc_to)
        self.ac_from = int(ac_from)
        self.ac_to = int(ac_to)
        self.ec_from = int(ec_from)
        self.ec_to = int(ec_to)
        self.acc = float(acc)


file_name = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/maker/round1/Gel.frag.1.r1.aa_vs_embryophyta_odb10/run_embryophyta_odb10/hmmer_output/16901at3193.out"


def hmmsearch_domtblout_parse(file_name):
    """
    http://eddylab.org/software/hmmer3/3.1b2/Userguide.pdf

    The domain hits table (protein search only)
    In protein search programs, the --domtblout option produces the domain hits table. There is one line for
    each domain. There may be more than one domain per sequence. The domain table has 22 whitespace-delimited
    fields followed by a free text target sequence description, as follows:

    (1) target name: The name of the target sequence or profile.
    (2) target accession: Accession of the target sequence or profile, or ’-’ if none is available.
    (3) tlen: Length of the target sequence or profile, in residues. This (together with the query length) is
    useful for interpreting where the domain coordinates (in subsequent columns) lie in the sequence.
    (4) query name: Name of the query sequence or profile.
    (5) accession: Accession of the target sequence or profile, or ’-’ if none is available.
    (6) qlen: Length of the query sequence or profile, in residues.
    (7) E-value: E-value of the overall sequence/profile comparison (including all domains).
    (8) score: Bit score of the overall sequence/profile comparison (including all domains), inclusive of a
    null2 bias composition correction to the score.
    (9) bias: The biased composition score correction that was applied to the bit score.
    (10) #: This domain’s number (1..ndom).
    (11) of: The total number of domains reported in the sequence, ndom.
    (12) c-Evalue: The “conditional E-value”, a permissive measure of how reliable this particular domain
    may be. The conditional E-value is calculated on a smaller search space than the independent Evalue.
    The conditional E-value uses the number of targets that pass the reporting thresholds. The
    null hypothesis test posed by the conditional E-value is as follows. Suppose that we believe that
    there is already sufficient evidence (from other domains) to identify the set of reported sequences as
    homologs of our query; now, how many additional domains would we expect to find with at least this
    particular domain’s bit score, if the rest of those reported sequences were random nonhomologous
    sequence (i.e. outside the other domain(s) that were sufficient to identified them as homologs in the
    first place)?
    (13) i-Evalue: The “independent E-value”, the E-value that the sequence/profile comparison would have
    received if this were the only domain envelope found in it, excluding any others. This is a stringent
    measure of how reliable this particular domain may be. The independent E-value uses the total
    number of targets in the target database.
    (14) score: The bit score for this domain.
    (15) bias: The biased composition (null2) score correction that was applied to the domain bit score.
    (16) from (hmm coord): The start of the MEA alignment of this domain with respect to the profile,
    numbered 1..N for a profile of N consensus positions.
    (17) to (hmm coord): The end of the MEA alignment of this domain with respect to the profile, numbered
    1..N for a profile of N consensus positions.
    (18) from (ali coord): The start of the MEA alignment of this domain with respect to the sequence,
    numbered 1..L for a sequence of L residues.
    (19) to (ali coord): The end of the MEA alignment of this domain with respect to the sequence, numbered 1..L
    for a sequence of L residues.
    (20) from (env coord): The start of the domain envelope on the sequence, numbered 1..L for a sequence of L residues.
    The envelope defines a subsequence for which their is substantial probability
    mass supporting a homologous domain, whether or not a single discrete alignment can be identified.
    The envelope may extend beyond the endpoints of the MEA alignment, and in fact often does, for
    weakly scoring domains.
    (21) to (env coord): The end of the domain envelope on the sequence, numbered 1..L for a sequence
    of L residues.
    (22) acc: The mean posterior probability of aligned residues in the MEA alignment; a measure of how
    reliable the overall alignment is (from 0 to 1, with 1.00 indicating a completely reliable alignment
    according to the model).
    (23) description of target: The remainder of the line is the target’s description line, as free text.

    q : query
    t : target
    fs : fill sequence
    d : this domain
    hc : hmm coord
    ac : ali coord
    ec : env corrd
    """
    fieldname = ["t_name", "t_accession", "t_len", "q_name", "q_accesstion", "q_len", "fs_evalue", "fs_score",
                 "fs_bias", "d_rank", "d_total_num", "d_cevalue", "d_ievalue", "d_score", "d_bias", "hc_from",
                 "hc_to", "ac_from", "ac_to", "ec_from", "ec_to", "acc", "description"]

    hmm_target_dict = {}
    with open(file_name, "r") as f:
        for each_line in f:
            # read line
            if re.match(r'^#', each_line):
                continue
            each_line = re.sub(r'\n', '', each_line)
            each_line_tuple = each_line.split(maxsplit=22)

            info = {}
            for i in range(len(fieldname)):
                info[fieldname[i]] = each_line_tuple[i]

            # save in object
            if not info['t_name'] in hmm_target_dict:
                hmm_target_dict[info['t_name']] = HmmTarget(name=info['t_name'], accession=info['t_accession'],
                                                            len=info['t_len'], fs_evalue=info['fs_evalue'],
                                                            fs_score=info['fs_score'], fs_bias=info['fs_bias'],
                                                            description=info['description'], HmmDomain_list=[])

            hmm_domin_tmp = HmmDomain(hmm_target_dict[info['t_name']], q_name=info['q_name'],
                                      q_accesstion=info['t_name'], q_len=info['q_len'], d_rank=info['d_rank'],
                                      d_total_num=info['d_total_num'], d_cevalue=info['d_cevalue'],
                                      d_ievalue=info['d_ievalue'], d_score=info['d_score'], d_bias=info['d_bias'],
                                      hc_from=info['hc_from'], hc_to=info['hc_to'], ac_from=info['ac_from'],
                                      ac_to=info['ac_to'], ec_from=info['ec_from'], ec_to=info['ec_to'],
                                      acc=info['acc'])

            hmm_target_dict[info['t_name']].HmmDomain_list.append(hmm_domin_tmp)

    return hmm_target_dict