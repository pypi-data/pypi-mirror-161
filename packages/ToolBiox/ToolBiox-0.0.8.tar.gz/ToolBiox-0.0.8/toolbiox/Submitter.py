if __name__ == '__main__':

    import argparse

    ###### argument parse
    parser = argparse.ArgumentParser(
        prog='Submitter',
    )

    subparsers = parser.add_subparsers(title='subcommands', dest="subcommand_name")

    # argparse for LocalMultiWork
    parser_a = subparsers.add_parser('LocalMultiWork',
                                     help='running many jobs by one machine')

    parser_a.add_argument('command_file', type=str, help='Path of command file for many jobs, each line is one command')
    parser_a.add_argument("-t", "--num_threads", help="num of threads (default:1)", default=1, type=int)
    parser_a.add_argument("-cwd", "--cwd_file",
                          help="Path of work dir file, each line in this file corresponds the cwd to each command in the command file.",
                          default=None, type=str)
    parser_a.add_argument("-l", "--log_file", help="path of log file", default=None, type=str)
    parser_a.add_argument("-s", "--silence", help="don't get error and stdout", action='store_true', default=False)
    parser_a.add_argument("-c", "--conda_env_mode", help="put cmd into a single shell file and with a given conda env",
                          default=None, type=str)

    # argparse for SGEMultiWork
    parser_a = subparsers.add_parser('SGEMultiWork',
                                     help='running many jobs by sge')

    parser_a.add_argument('command_file', type=str, help='Path of command file for many jobs, each line is one command')
    parser_a.add_argument("-wd", "--submit_dir", help="Path of submiter dir.", default=None, type=str)
    parser_a.add_argument("-cwd", "--cwd_file",
                          help="Path of work dir file, each line in this file corresponds the cwd to each command in the command file.",
                          default=None, type=str)
    parser_a.add_argument("-bq", "--base_qsub_args", help="base args for qsub", default="-V -b y -cwd -q all.q@@xyx",
                          type=str)
    parser_a.add_argument("-aq", "--add_qsub_args", help="add args for qsub", default="", type=str)
    parser_a.add_argument("-c", "--conda_env_mode", help="put cmd into a single shell file and with a given conda env",
                          default=None, type=str)

    args = parser.parse_args()
    args_dict = vars(args)

    # ---------------------------------------------------------
    #### command detail

    if args_dict["subcommand_name"] == "LocalMultiWork":
        import subprocess
        from multiprocessing import Pool
        import logging
        import time
        import os
        from toolbiox.lib.common.os import mkdir, cmd_run, multiprocess_running


        def log_print(print_string):
            time_tmp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print("%s\t\t\t%s\n" % (time_tmp, print_string))


        def logging_init(program_name, log_file=None):
            # create logger with 'program_name'
            logger = logging.getLogger(program_name)
            logger.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            if not log_file is None:
                # create file handler which logs even debug messages
                fh = logging.FileHandler(log_file)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(formatter)
                logger.addHandler(fh)
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(ch)

            return logger


        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]


        def cmd_run_rltime(cmd_string, stdout_file, stderr_file, cwd=None, silence=False):
            if silence:
                returncode = subprocess.call(cmd_string, cwd=cwd, shell=True)
            else:
                with open(stdout_file, 'w') as stdout_f:
                    with open(stderr_file, 'w') as stderr_f:
                        returncode = subprocess.call(cmd_string, cwd=cwd, shell=True, stdout=stdout_f, stderr=stderr_f)
            return returncode


        # def multiprocess_running(f, args_list, pool_num, slience=True):
        #     """
        #
        #     :param f: function name
        #     :param args_list: a list include every args in a tuple
        #     :param pool_num: process num of running at sametime
        #     :param slience:
        #     :return:
        #     """
        #
        #     if pool_num == 0:
        #         p = Pool()
        #     else:
        #         p = Pool(pool_num)
        #     p_dict = {}
        #     num = 0
        #
        #     for i in args_list:
        #         p_dict['ID_' + str(num)] = {
        #             'args': i,
        #             'output': None,
        #             'success': None,
        #             'p_object': p.apply_async(f, args=i)
        #         }
        #         num = num + 1
        #
        #     if not slience:
        #         print('Waiting for all subprocesses done...')
        #     p.close()
        #     p.join()
        #     if not slience:
        #         print('All subprocesses done.')
        #
        #     for i in p_dict:
        #         p_dict[i]['output'] = p_dict[i]['p_object'].get()
        #         p_dict[i]['success'] = p_dict[i]['p_object']._success
        #         del p_dict[i]['p_object']
        #
        #     return p_dict

        """
        class abc():
            pass
        
        args=abc()
        args.command_file = "/lustre/home/xuyuxing/Database/Gel/genome/annotation/pasa/evm/commands.list"
        args.num_threads = 56
        args.cwd_file = None
        args.log_file = None
        args.conda_env_mode = "maker_p"
        """

        logger = logging_init("LocalMultiWork", args.log_file)

        logger.info("Parsing cmd and cwd file")
        command_dict = {}
        num = 0
        with open(args.command_file, 'r') as f:
            for each_line in f.readlines():
                ID_tmp = "ID_" + str(num)
                each_line = each_line.strip()
                command_dict[ID_tmp] = {"cmd": each_line}
                num = num + 1

        logger.info("Parsed cmd file")
        if not args.cwd_file is None:
            logger.info("Found cwd file")
            num = 0
            with open(args.cwd_file, 'r') as f:
                for each_line in f.readlines():
                    ID_tmp = "ID_" + str(num)
                    each_line = each_line.strip()
                    command_dict[ID_tmp]["cwd"] = each_line
                    num = num + 1
            logger.info("Parsed cwd file")
        else:
            logger.info("Not Found cwd file, cmd will running in current word dir")
            for ID_tmp in command_dict:
                command_dict[ID_tmp]["cwd"] = os.getcwd()

        if args.conda_env_mode:
            logger.info("Parsed conda env mode")
            tmp_dir = os.getcwd() + "/tmp"
            mkdir(tmp_dir)
            for cmd_id in command_dict:
                tmp_file_name = tmp_dir + "/" + cmd_id + ".sh"
                with open(tmp_file_name, 'w') as f:
                    f.write("source activate %s\n" % args.conda_env_mode)
                    f.write("cd %s\n" % command_dict[cmd_id]['cwd'])
                    f.write("%s\n" % command_dict[cmd_id]['cmd'])
                    f.write("conda deactivate\n")
                command_dict[cmd_id]['cmd'] = "bash %s" % tmp_file_name

        args_list = []
        for ID_tmp in command_dict:
            cmd = command_dict[ID_tmp]['cmd']
            cwd = command_dict[ID_tmp]['cwd']
            stdout = cwd + "/" + ID_tmp + ".out"
            stderr = cwd + "/" + ID_tmp + ".err"
            args_tuple = (cmd, stdout, stderr, cwd, args.silence)
            args_list.append(args_tuple)

        cmd_result = multiprocess_running(cmd_run_rltime, args_list, args.num_threads, log_file=args.log_file)

        # logger.info("#############cmd running#############")
        # round_num = 0
        # for round_tmp in chunks(list(command_dict.keys()), args.num_threads * 1):
        #     logger.info("Round %d:" % round_num)
        #     logger.info("Included %s to %s" % (round_tmp[0], round_tmp[-1]))
        #
        #     args_list = []
        #     for ID_tmp in round_tmp:
        #         cmd = command_dict[ID_tmp]['cmd']
        #         cwd = command_dict[ID_tmp]['cwd']
        #         stdout = cwd + "/" + ID_tmp + ".out"
        #         stderr = cwd + "/" + ID_tmp + ".err"
        #         args_tuple = (cmd, stdout, stderr, cwd)
        #         args_list.append(args_tuple)
        #
        #     cmd_result = multiprocess_running(cmd_run_rltime, args_list, args.num_threads)
        #
        #     tmp_num = 0
        #     for ID_tmp in cmd_result:
        #         raw_ID_tmp = round_tmp[tmp_num]
        #         sucess_flag = cmd_result[ID_tmp]['success']
        #         if sucess_flag:
        #             # print("%s is OK" % raw_ID_tmp)
        #             logger.info("%s is OK" % raw_ID_tmp)
        #         else:
        #             logger.info("%s is BAD" % raw_ID_tmp)
        #         tmp_num = tmp_num + 1
        #
        #     round_num = round_num + 1
        #
        # logger.info("#############All Finished#############")

    elif args_dict["subcommand_name"] == "SGEMultiWork":
        """
        class abc():
            pass

        args=abc()
        args.command_file = "/lustre/home/xuyuxing/Database/Phelipanche/annotation/evm/est/cufflinks/cmd.list"
        args.submit_dir = "/lustre/home/xuyuxing/Database/Phelipanche/annotation/evm/est/cufflinks"
        args.base_qsub_args = "-V -b y -cwd -q all.q@@xyx"
        args.add_qsub_args = ""
        args.conda_env_mode = "map_tools"
        args.cwd_file = None
        """
        import os
        import re
        from toolbiox.lib.xuyuxing.base.base_function import mkdir, cmd_run

        if args.submit_dir is None:
            args.submit_dir = os.getcwd()
        else:
            args.submit_dir = os.path.abspath(args.submit_dir)
        tmp_dir = args.submit_dir + "/job_submit_tmp"
        mkdir(tmp_dir, False)

        command_dict = {}
        num = 0
        with open(args.command_file, 'r') as f:
            for each_line in f.readlines():
                ID_tmp = "ID_" + str(num)
                each_line = each_line.strip()
                command_dict[ID_tmp] = {"cmd": each_line}
                num = num + 1

        if not args.cwd_file is None:
            num = 0
            with open(args.cwd_file, 'r') as f:
                for each_line in f.readlines():
                    ID_tmp = "ID_" + str(num)
                    each_line = each_line.strip()
                    command_dict[ID_tmp]["cwd"] = each_line
                    num = num + 1
        else:
            for ID_tmp in command_dict:
                command_dict[ID_tmp]["cwd"] = args.submit_dir

        sge_jobs_dict = {}
        with open(args.command_file, 'r') as f:
            for cmd_id in command_dict:
                tmp_file_name = tmp_dir + "/" + cmd_id + ".sh"
                with open(tmp_file_name, 'w') as o:
                    o.write("source activate %s\n" % args.conda_env_mode)
                    o.write("cd %s\n" % command_dict[cmd_id]['cwd'])
                    o.write("%s\n" % command_dict[cmd_id]['cmd'])
                    o.write("conda deactivate\n")

                cmd_string = "qsub %s %s bash %s" % (args.base_qsub_args, args.add_qsub_args, tmp_file_name)

                returncode, output, error = cmd_run(cmd_string, cwd=args.submit_dir, retry_max=1, silence=True)
                # print(output)

                job_id, job_name = re.findall(r'Your job (\d+) \("(\S+)"\) has been submitted', output)[0]
                sge_jobs_dict[job_id] = (job_id, job_name)

        all_job_done = False

        while not all_job_done:
            all_job_done = True
            for job_id in sge_jobs_dict:
                cmd_string = 'qstat -j %s' % job_id
                returncode, output, error = cmd_run(cmd_string, cwd=args.submit_dir, retry_max=1, silence=True,
                                                    log_file=None)
                if not error == 'Following jobs do not exist: \n%s\n' % job_id:
                    all_job_done = False

        print("all %d jobs finished!" % len(sge_jobs_dict))
