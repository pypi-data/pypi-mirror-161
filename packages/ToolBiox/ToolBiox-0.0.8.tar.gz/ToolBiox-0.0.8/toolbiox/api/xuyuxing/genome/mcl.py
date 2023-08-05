from toolbiox.lib.common.os import mkdir, rmdir, cmd_run
from toolbiox.api.xuyuxing.file_parser.fileIO import tsv_file_parse
import uuid
import os


def gene_mcl(input_gene_list, inflation=1.5, name_attr='name', seq_attr='model_aa_seq', work_dir='/tmp', cpu_num=5,
             force_redo=False, keep_flag=False, diamond_flag=False):
    mkdir(work_dir, True)

    if not force_redo:
        for file in os.listdir(work_dir):
            if len(file) == 32 and os.path.exists(work_dir + "/" + file + "/input.faa") and os.path.exists(
                    work_dir + "/" + file + "/all_to_all.bls") and os.path.exists(
                work_dir + "/" + file + "/subject.seq.abc") and os.path.exists(
                work_dir + "/" + file + "/subject.seq.mci") and os.path.exists(
                work_dir + "/" + file + "/subject.seq.tab"):

                tmp_dir = work_dir + "/" + file
                mcl_output = "%s/subject.%.1f.mcl.out" % (tmp_dir, inflation)

                if os.path.exists(mcl_output):
                    mcl_output_dir = tsv_file_parse(mcl_output)
                else:
                    mcl_mci_file = tmp_dir + "/subject.seq.mci"
                    mcl_tab_file = tmp_dir + "/subject.seq.tab"
                    mcl_output = "%s/subject.%.1f.mcl.out" % (tmp_dir, inflation)
                    cmd_string = "mcl %s -I %s -use-tab %s -o %s" % (mcl_mci_file, inflation, mcl_tab_file, mcl_output)
                    cmd_run(cmd_string, cwd=tmp_dir)
                    mcl_output_dir = tsv_file_parse(mcl_output)

                return mcl_output_dir

    tmp_dir = work_dir + "/" + uuid.uuid1().hex
    mkdir(tmp_dir, False)

    input_fasta_file = tmp_dir + "/input.faa"
    with open(input_fasta_file, 'w') as f:
        for gene in input_gene_list:
            f.write(">%s\n%s\n" % (getattr(gene, name_attr), getattr(gene, seq_attr)))

    # all to all blast
    if not diamond_flag:
        cmd_string = "makeblastdb -in %s -dbtype prot" % input_fasta_file
        cmd_run(cmd_string)

        all_to_all_blast = tmp_dir + "/all_to_all.bls"
        cmd_string = "blastp -query %s -db %s -out %s -evalue 1e-5 -outfmt 6 -num_threads %d" % (
            input_fasta_file, input_fasta_file, all_to_all_blast, cpu_num)
        cmd_run(cmd_string, cwd=tmp_dir)
    else:
        cmd_string = "diamond makedb --in %s --db %s" % (input_fasta_file, input_fasta_file)
        cmd_run(cmd_string)
        diamond_db = input_fasta_file + ".dmnd"

        all_to_all_blast = tmp_dir + "/all_to_all.bls"

        cmd_string = "diamond blastp -q %s -d %s -o %s -k 500 -e 1e-5 -f 6 -p %d" % (
            input_fasta_file, diamond_db, all_to_all_blast, cpu_num)
        cmd_run(cmd_string, cwd=tmp_dir)


    # mcl pre
    tsv_dict = tsv_file_parse(all_to_all_blast, fields="1,2,11")
    mcl_abc_file = tmp_dir + "/subject.seq.abc"
    with open(mcl_abc_file, "w") as f:
        for a, b, c in [tsv_dict[i] for i in tsv_dict]:
            f.write(a + "\t" + b + "\t" + c + "\n")

    # mcl
    mcl_mci_file = tmp_dir + "/subject.seq.mci"
    mcl_tab_file = tmp_dir + "/subject.seq.tab"
    cmd_string = "mcxload -abc %s --stream-mirror --stream-neg-log10 -stream-tf 'ceil(200)' -o %s -write-tab %s" % (
        mcl_abc_file, mcl_mci_file, mcl_tab_file)
    cmd_run(cmd_string, cwd=tmp_dir)

    mcl_output = "%s/subject.%.1f.mcl.out" % (tmp_dir, inflation)
    cmd_string = "mcl %s -I %s -use-tab %s -o %s" % (mcl_mci_file, inflation, mcl_tab_file, mcl_output)
    cmd_run(cmd_string, cwd=tmp_dir)
    mcl_output_dir = tsv_file_parse(mcl_output)

    if not keep_flag:
        rmdir(tmp_dir)

    return mcl_output_dir
