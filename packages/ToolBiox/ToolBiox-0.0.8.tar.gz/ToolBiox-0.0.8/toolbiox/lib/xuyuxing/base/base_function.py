import subprocess
import os
import uuid
import shutil
import time
from multiprocessing import Pool, TimeoutError
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

from toolbiox.lib.common.os import *
from toolbiox.lib.common.util import *

__author__ = 'Yuxing Xu'


# time
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


# file and dir


def merge_file(input_file_list, output_file):
    with open(output_file, 'w') as f:
        for input_file in input_file_list:
            fr = open(input_file, 'r').read()
            if len(fr) > 0 and fr[-1] != '\n':
                fr = fr+'\n'
            f.write(fr)


def get_FileAccessTime(filePath):
    t = os.path.getatime(filePath)
    return TimeStampToTime(t)


def get_FileCreateTime(filePath):
    t = os.path.getctime(filePath)
    return TimeStampToTime(t)


def get_FileModifyTime(filePath):
    t = os.path.getmtime(filePath)
    return TimeStampToTime(t)


def print_tar_gz_info(tar_file):
    import tarfile
    tar = tarfile.open(tar_file, "r:gz")
    for tarinfo in tar:
        print(tarinfo.name, "is", tarinfo.size,
              "bytes in size and is ", end="")
        if tarinfo.isreg():
            print("a regular file.")
        elif tarinfo.isdir():
            print("a directory.")
        else:
            print("something else.")
    tar.close()


# running bash


def cmd_run_rltime(cmd_string, stdout_file, stderr_file, cwd=None):
    with open(stdout_file, 'w') as stdout_f:
        with open(stderr_file, 'w') as stderr_f:
            returncode = subprocess.call(
                cmd_string, cwd=cwd, shell=True, stdout=stdout_f, stderr=stderr_f)
    return returncode


def cmd_open(cmd_string, cwd=None):
    """
    open file by a shell cmd, such as zcat or samtools view
    :param cmd_string:
    :param cwd:
    :return:
    """
    p = subprocess.Popen(cmd_string, shell=True,
                         stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)
    done = 0
    while not done:
        line_tmp = p.stdout.readline().decode()
        yield line_tmp
        if line_tmp == "":
            done = 1


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


# def multiprocess_running(f, args_list, pool_num, log_file=None, silence=True, args_id_list=None, timeout=None):
#     """
#     :param f: function name
#     :param args_list: a list include every args in a tuple
#     :param pool_num: process num of running at sametime
#     :param silence:
#     :return:

#     example

#     def f(x, y):
#         time.sleep(1)
#         return x * y

#     args_list = list(zip(range(1,200),range(2,201)))
#     pool_num = 5

#     multiprocess_running(f, args_list, pool_num, log_file='/lustre/home/xuyuxing/Work/Other/saif/Meth/tmp/log')

#     """

#     num_tasks = len(list(args_list))

#     module_log = logging_init(f.__name__, log_file)
#     if not silence:
#         print('args_list have %d object and pool_num is %d' %
#               (num_tasks, pool_num))
#     module_log.info('running with mulitprocess')
#     module_log.info('args_list have %d object and pool_num is %d' %
#                     (num_tasks, pool_num))

#     p_dict = {}

#     if len(args_list) > 0:

#         f_with_para = partial(get_more_para, f)
#         abortable_func = partial(abortable_worker, f_with_para, timeout=timeout)

#         #    def get_more_para(para_tuple):
#         #        return f(*para_tuple)

#         #    args_list_unziped = zip(*args_list)

#         start_time = time.time()

#         if not silence:
#             print('Begin: ')
#         module_log.info('Begin: ')

#         with Pool(processes=pool_num, maxtasksperchild=1) as pool:
#             # for i, output in enumerate(pool.imap_unordered(f_with_para, args_list, chunksize=1)):
#             it = pool.imap(abortable_func, args_list, chunksize=1)
#             i=-1
#             while 1:
#                 i+=1
#                 # print(i)

#                 try:
#                     output = it.next()

#                     if args_id_list:
#                         job_id = args_id_list[i]
#                     else:
#                         job_id = 'ID_' + str(i)

#                     if output == "Aborting due to timeout":
#                         p_dict[job_id] = {
#                             'args': args_list[i],
#                             'output': None,
#                             'error': "timeout"
#                         }
#                     else:
#                         p_dict[job_id] = {
#                             'args': args_list[i],
#                             'output': output,
#                             'error': None
#                         }

#                     # print(i)
#                     round_time = time.time()
#                     if round_time - start_time > 5:
#                         if not silence:
#                             print('%d/%d %.2f%% parsed' %
#                                 (i, num_tasks, i / num_tasks * 100))
#                         module_log.info('%d/%d %.2f%% parsed' %
#                                         (i, num_tasks, i / num_tasks * 100))
#                         start_time = round_time

#                     # module_log.info('%d/%d %.2f%% parsed' % (i, num_tasks, i / num_tasks * 100))

#                 except StopIteration:
#                     break


#         module_log.info('%d/%d %.2f%% parsed' %
#                         (i, num_tasks, i / num_tasks * 100))
#         module_log.info('All args_list task finished')

#         if not silence:
#             print('%d/%d %.2f%% parsed' % (i, num_tasks, i / num_tasks * 100))
#             print('All args_list task finished')

#     del module_log.handlers[:]

#     return p_dict


if __name__ == '__main__':
    from multiprocessing import Queue

    share_data = [1, 2, 3, 4, 5, 6, 7]

    share_data_queue = Queue()

    from time import sleep

    def f(x):
        sleep(x)
        return x

    args_list = [(1,), (10,), (2,), (3,), (4,), (5,), (6,), (7,), (8,)]

    args_id_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

    cmd_result = multiprocess_running(
        f, args_list, 3, args_id_list=args_id_list, timeout=5)
