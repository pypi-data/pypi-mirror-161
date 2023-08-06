import os
from toolbiox.lib.common.util import logging_init
from toolbiox.lib.common.os import cmd_run, mkdir
from toolbiox.api.xuyuxing.genome.maker_config_file_code import write_maker_config, write_maker_evaluate_anno_shell, write_maker_to_snap_augustus_shell, write_inherit_maker_gff_shell


class Maker_Job(object):
    def __init__(self, args):
        # parse argument
        self.args = args

    def first_round(self, work_dir):
        mkdir(work_dir, True)
        config_file = work_dir + "/maker_config.txt"

        genome_file = work_dir+"/genome.fasta"
        os.symlink(os.path.abspath(self.args.genome_file), genome_file)

        repeat_file = work_dir+"/repeat.fasta"
        os.symlink(os.path.abspath(self.args.repeat_file), repeat_file)

        est_file = work_dir+"/est.fasta"
        os.symlink(os.path.abspath(self.args.est_file), est_file)

        protein_file = work_dir+"/protein.fasta"
        os.symlink(os.path.abspath(self.args.protein_file), protein_file)

        rRNA_file = work_dir+"/rRNA.fasta"
        os.symlink(os.path.abspath(self.args.rrna_file), rRNA_file)

        repeat_protein = work_dir+"/repeat_protein.fasta"
        os.symlink(os.path.abspath(self.args.repeat_protein), repeat_protein)

        TMP_dir = work_dir+"/TMP"
        mkdir(TMP_dir)

        write_maker_config(
            config_file=config_file,
            genome=genome_file,
            est=est_file,
            protein=protein_file,
            rmlib=repeat_file,
            repeat_protein=repeat_protein,
            augustus_species=self.args.augustus_species,
            est2genome=1,
            protein2genome=1,
            snoscan_rrna=rRNA_file,
            TMP=TMP_dir,
        )

        print("Please running command:")
        print("cd %s" % work_dir)
        print("source activate maker_p")
        print("nohup mpiexec -n 56 maker --ignore_nfs_tmp maker_config.txt > nohup.txt &")

    def evaluate_anno(self, maker_output_dir):
        """
        maker_output_dir = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output"
        """

        evaluate_anno_shell_file = maker_output_dir + "/evaluate_anno.sh"

        index_log_file = maker_output_dir + '/genome_master_datastore_index.log'

        write_maker_evaluate_anno_shell(
            evaluate_anno_shell_file, index_log_file)

        cmd_run_string = "bash " + evaluate_anno_shell_file

        cmd_run(cmd_run_string, cwd=maker_output_dir,
                retry_max=1, silence=True, log_file=None)

    def to_next_round(self, maker_output_dir):
        """
        maker_output_dir = "/lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output"
        """
        to_next_dir = maker_output_dir + "/to_next"
        mkdir(to_next_dir, True)
        maker_to_snap_augustus_shell_file = to_next_dir + "/maker_to_snap_augustus.sh"
        index_log_file = maker_output_dir + '/genome_master_datastore_index.log'

        # train snap and augustus
        write_maker_to_snap_augustus_shell(maker_to_snap_augustus_shell_file)

        cmd_run_string = "bash %s %s %s" % (
            maker_to_snap_augustus_shell_file, self.args.tag, index_log_file)

        cmd_run(cmd_run_string, cwd=to_next_dir,
                retry_max=1, silence=True, log_file=None)

        # rewrite gff to next round
        inherit_maker_gff_shell_file = maker_output_dir + "/inherit_maker_gff.sh"
        write_inherit_maker_gff_shell(inherit_maker_gff_shell_file)

        cmd_run_string = "bash " + inherit_maker_gff_shell_file

        cmd_run(cmd_run_string, cwd=maker_output_dir,
                retry_max=1, silence=True, log_file=None)

        print("est_gff: %s/for_next.est2genome.gff" % maker_output_dir)
        print("protein_gff: %s/for_next.protein2genome.gff" % maker_output_dir)
        print("rm_gff: %s/for_next.repeats.gff" % maker_output_dir)
        print("snaphmm: %s/to_next/%s.zff.length50_aed0.25.hmm" %
              (maker_output_dir, self.args.tag))
        print("augustus_species: %s" % self.args.tag)

    def improve_round(self, work_dir):
        mkdir(work_dir, True)
        config_file = work_dir + "/maker_config.txt"

        genome_file = work_dir+"/genome.fasta"
        os.symlink(os.path.abspath(self.args.genome_file), genome_file)

        rm_gff = work_dir+"/rm.gff"
        os.symlink(os.path.abspath(self.args.rm_gff), rm_gff)

        est_gff = work_dir+"/est.gff"
        os.symlink(os.path.abspath(self.args.est_gff), est_gff)

        protein_gff = work_dir+"/protein.gff"
        os.symlink(os.path.abspath(self.args.protein_gff), protein_gff)

        snaphmm = work_dir+"/snaphmm.hmm"
        os.symlink(os.path.abspath(self.args.snaphmm), snaphmm)

        rRNA_file = work_dir+"/rRNA.fasta"
        os.symlink(os.path.abspath(self.args.rrna_file), rRNA_file)

        TMP_dir = work_dir+"/TMP"
        mkdir(TMP_dir)

        write_maker_config(
            config_file=config_file,
            genome=genome_file,
            est_gff=est_gff,
            protein_gff=protein_gff,
            rm_gff=rm_gff,
            snaphmm=snaphmm,
            augustus_species=self.args.augustus_species,
            est2genome=0,
            protein2genome=0,
            snoscan_rrna=rRNA_file,
            TMP=TMP_dir,
        )

        print("Please running command:")
        print("cd %s" % work_dir)
        print("source activate maker_p")
        print("nohup mpiexec -n 56 maker --ignore_nfs_tmp maker_config.txt > nohup.txt &")


def maker_main(args):
    mkdir(args.work_dir, True)
    log_file = args.work_dir + "/log.txt"

    logger = logging_init("maker main", log_file)

    args_info_string = "Argument list:\n"
    attrs = vars(args)

    for item in attrs.items():
        args_info_string = args_info_string + ("%s: %s\n" % item)

    logger.info(args_info_string)

    maker_job = Maker_Job(args)

    if args.job == 'first_anno':
        # first round
        logger.info("Running first_anno at %s" % args.work_dir)
        maker_job.first_round(args.work_dir)

    elif args.job == 'evaluate_anno':
        # evaluate_anno
        logger.info("Running evaluate_anno at %s" % args.work_dir)
        maker_job.evaluate_anno(args.work_dir)

    elif args.job == 'to_next_round':
        # evaluate_anno
        logger.info("Running to_next_round at %s" % args.work_dir)
        maker_job.to_next_round(args.work_dir)

    elif args.job == 'improve_anno':
        # evaluate_anno
        logger.info("Running improve_anno at %s" % args.work_dir)
        maker_job.improve_round(args.work_dir)


if __name__ == '__main__':
    # first round
    # need a configure file

    """
    [Parameter]
    num_threads = 56

    [Paths]
    tag = Llv
    genome_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/Llv.genome.nt.1.0.fasta
    repeat_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker_p/Llv_maker_p/allRepeats.lib
    est_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/trinity/trinity_output/Trinity.fasta
    protein_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/close.aa.fasta
    rRNA_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/rRNA/rRNA.no_ITS.fa
    augustus_species = tomato
    repeat_protein = /lustre/home/xuyuxing/Database/Phelipanche/annotation/maker_p/repeat/Tpase/Tpases020812
    """

    # python ~/python_project/Genome_work_tools/GenAnno.py EasyMaker -j first_anno -c maker.config -d /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker
    # nohup mpiexec -n 56 maker --ignore_nfs_tmp maker.config > nohup.txt &

    # python ~/python_project/Genome_work_tools/GenAnno.py EasyMaker -d /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output -j evaluate_anno
    # python ~/python_project/Genome_work_tools/GenAnno.py EasyMaker -d /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output -j to_next_round -t Llv_v1

    """
    [Parameter]
    num_threads = 56

    [Paths]
    tag = Llv
    genome_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/Llv.genome.nt.1.0.fasta
    est_gff = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output/for_next.est2genome.gff
    protein_gff = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output/for_next.protein2genome.gff
    rm_gff = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output/for_next.repeats.gff
    snaphmm = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/maker_work/genome.maker.output/to_next/Llv_v1.zff.length50_aed0.25.hmm
    augustus_species = Llv_v1
    rRNA_file = /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/rRNA/rRNA.no_ITS.fa
    """

    # python ~/python_project/Genome_work_tools/GenAnno.py EasyMaker -j improve_anno -c maker_r2.config -d /lustre/home/xuyuxing/Database/Lindenbergia/genome/annotation/maker/round2
    # nohup mpiexec -n 56 maker --ignore_nfs_tmp maker.config > nohup.txt &
