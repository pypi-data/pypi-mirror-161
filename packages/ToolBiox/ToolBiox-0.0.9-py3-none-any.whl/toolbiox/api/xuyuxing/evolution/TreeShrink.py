import os
import re
import shutil
from toolbiox.config import treeshrink_path
from toolbiox.lib.common.os import cmd_run


def treeshrink_running(tree_file, outdir, q_value=0.05, keep=False):
    if os.path.exists(outdir):
        shutil.rmtree(outdir)

    cmd_string = "%s -t %s -q %s -o %s" % (treeshrink_path, tree_file, str(q_value), outdir)
    cmd_run(cmd_string, silence=True)

    shrunk_list = []
    for file in os.listdir(outdir):
        match_Obj = re.match('^.*\_%s\.txt$' % str(q_value), file)
        if match_Obj:
            with open(outdir + "/" + file, 'r') as f:
                for each_line in f:
                    each_line = each_line.strip()
                    info = each_line.split("\t")
                    shrunk_list.extend(info)

    shrunk_list = list(set(shrunk_list))

    if not keep:
        shutil.rmtree(outdir)

    return shrunk_list


