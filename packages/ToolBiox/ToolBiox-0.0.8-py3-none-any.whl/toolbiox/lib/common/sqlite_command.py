"""
This module work to help load data to sqlite.
usage:
#
import toolbiox.lib.sqlite_command as sql
#
class:

function:
    check_sql_table
    check_table_columns
    init_sql_db
    init_sql_db_many_table
    insert_one_record_to_sql_table
    dict2sql_table
    sql_table2dict
    sql_table_row_num
log:
    Yuxing Xu
    2018.02.05  new module
    2018.02.05  update module
"""
import sqlite3
import codecs
import pickle
from toolbiox.config import sqlite_temp_store_directory

# from retry import retry


def check_sql_table(db_file):
    conn = sqlite3.connect(db_file)
    table_list = conn.execute(
        'SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()
    conn.close()

    output = []
    for i in table_list:
        output.append(i[0])
    return tuple(output)


def check_table_columns(db_file, table_name):
    conn = sqlite3.connect(db_file)
    content = conn.execute('PRAGMA table_info(' + table_name + ')').fetchall()
    conn.close()

    table_head = []
    for i in content:
        table_head.append(i[1])
    return tuple(table_head)


def all_database_stat(db_file):
    conn = sqlite3.connect(db_file)
    table_list = conn.execute(
        'SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()

    output = []
    for i in table_list:
        output.append(i[0])
    output = tuple(output)

    db_stat = {}
    for i in output:
        db_stat[i] = {}
        table_record_num = conn.execute('SELECT count(*) FROM ' + i).fetchall()
        db_stat[i]["record_num"] = table_record_num[0][0]
        content = conn.execute('PRAGMA table_info(' + i + ')').fetchall()
        table_head = []
        for j in content:
            table_head.append(j[1])
        db_stat[i]["column"] = table_head

    conn.close()
    return db_stat


def init_sql_db(db_file, table_name, column_name_list, remove_old_db=True):
    import os
    from toolbiox.lib.common.os import cmd_run
    if remove_old_db is True:
        if os.path.exists(db_file):
            cmd_run("rm %s" % db_file)

    conn = sqlite3.connect(db_file)

    create_cmd = '''CREATE TABLE ''' + table_name + " ("
    for column_name in column_name_list:
        create_cmd = create_cmd + "\"" + column_name + "\", "
    create_cmd = create_cmd.rstrip(", ")
    create_cmd = create_cmd + ")"
    conn.execute(create_cmd)

    conn.commit()
    conn.close()


def init_sql_db_many_table(db_file, table_columns_dict, remove_old_db=True):
    import os
    from toolbiox.lib.common.os import cmd_run
    if remove_old_db and os.path.exists(db_file):
        cmd_run("rm %s" % db_file)

    conn = sqlite3.connect(db_file)

    for table_name in table_columns_dict:
        create_cmd = "CREATE TABLE \"" + table_name + "\" ("
        for column_name in table_columns_dict[table_name]:
            create_cmd = create_cmd + column_name + ", "
        create_cmd = create_cmd.rstrip(", ")
        create_cmd = create_cmd + ")"
        conn.execute(create_cmd)

    conn.commit()
    conn.close()


def insert_one_record_to_sql_table(data_tuple, columns_list_tuple, db_file, table_name):
    conn = sqlite3.connect(db_file)
    insert_cmd = '''INSERT INTO ''' + table_name + " " + tuple(columns_list_tuple).__str__() \
                 + ''' VALUES ''' + tuple(data_tuple).__str__()
    conn.execute(insert_cmd)
    conn.commit()
    conn.close()


def dict2sql_table(data_dict, table_columns_dict, db_file, table_name):
    column_name = table_columns_dict[table_name]

    if len(column_name) != len(data_dict[0]):
        raise ValueError

    def iter_sql_insert(data_dict):
        for i in data_dict:
            table_insert = data_dict[i]
            yield tuple(table_insert)

    conn = sqlite3.connect(db_file)
    insert_cmd = '''INSERT INTO ''' + table_name + \
        ''' VALUES (''' + "?," * len(column_name)
    insert_cmd = insert_cmd.rstrip(",")
    insert_cmd = insert_cmd + ")"
    conn.executemany(insert_cmd, iter_sql_insert(data_dict))
    conn.commit()
    conn.close()


def sql_table2dict(db_file, table_name, top=0, key="", print_if=False):
    table_head = check_table_columns(db_file, table_name)

    conn = sqlite3.connect(db_file)
    if not top == 0:
        content = conn.execute(
            'SELECT * FROM ' + table_name + ' LIMIT ?', (top,)).fetchall()
    else:
        content = conn.execute('SELECT * FROM ' + table_name).fetchall()

    conn.close()

    output_dict = {}
    num = 0
    for i in content:
        num = num + 1
        if key == "":
            output_dict[num] = i
        else:
            key_value = i[table_head.index(key)]
            output_dict[key_value] = i

    if print_if is True:
        printer = ""
        for i in table_head:
            printer = printer + i + "\t"
        printer = printer.rstrip("\t") + "\n" + "---" + "\n"
        for i in content:
            for j in i:
                printer = printer + str(j) + "\t"
            printer = printer.rstrip("\t") + "\n"

    return output_dict, table_head


def sql_table_row_num(db_file, table_name):
    conn = sqlite3.connect(db_file)
    record_len = conn.execute("select count(*) from %s" %
                              table_name).fetchall()[0][0]
    conn.close()
    return record_len


def drop_index(db_file_name, index_name):
    conn = sqlite3.connect(db_file_name)
    conn.execute("DROP INDEX %s" % index_name)
    conn.commit()
    conn.close()


def build_index(db_file_name, table_name, key_col_name):
    conn = sqlite3.connect(db_file_name)
    conn.execute("PRAGMA temp_store_directory = \'%s\'" %
                 sqlite_temp_store_directory)
    conn.execute("CREATE UNIQUE INDEX %s_index on %s (\"%s\")" %
                 (table_name, table_name, key_col_name))
    conn.commit()
    conn.close()


def drop_table(db_file_name, table_name):
    conn = sqlite3.connect(db_file_name)
    conn.execute("DROP TABLE %s" % table_name)
    conn.commit()
    conn.close()


def dict_context_yield(list_input):
    for query in list_input:
        yield query


# @retry()
def sqlite_write(record_list, db_file, table_name, columns_list):
    """
    :param record_list:
            record_list=[("A1","B1","C1","D1","E1"),("A2","B2","C2","D2","E2"),...]
    :param db_file:
    :param table_name: table should be inited
    :param columns_list:
            columns_list = ["A","B","C","D","E"]
    :return:
    """
    conn = sqlite3.connect(db_file)
    insert_cmd = '''INSERT INTO "''' + table_name + \
        '''" VALUES (''' + "?," * len(columns_list)
    insert_cmd = insert_cmd.rstrip(",")
    insert_cmd = insert_cmd + ")"
    conn.execute("PRAGMA temp_store_directory = \'%s\'" %
                 sqlite_temp_store_directory)
    conn.executemany(insert_cmd, dict_context_yield(record_list))

    conn.commit()
    conn.close()


def dict_context_yield_for_update(list_input):
    for key, value in list_input:
        yield (value, key)

# @retry()


def sqlite_update(db_file, table_name, key_col, value_col, key_value_tuple_list):
    """
    :param key_col = 'name'
    :param value_col = 'age'
    :param key_value_tuple: [("Mark Arnold", 30)]
    :return:
    """
    conn = sqlite3.connect(db_file)
    update_cmd = '''UPDATE %s SET %s = ? WHERE %s = ?''' % (
        table_name, value_col, key_col)

    conn.executemany(
        update_cmd, dict_context_yield_for_update(key_value_tuple_list))

    conn.commit()
    conn.close()


def sqlite_delete(db_file, table_name, key_name=None, value_tuple=None):
    if key_name is None:
        conn = sqlite3.connect(db_file)
        # print("SELECT %s FROM %s" % (column_string, table_name))
        content = conn.execute("DELETE FROM \"%s\"" %
                               (table_name)).fetchall()
        conn.commit()
        conn.close()

    else:
        conn = sqlite3.connect(db_file)
        value_tuple = tuple(value_tuple)
        if len(value_tuple) == 1:
            content = conn.execute(
                "DELETE FROM \"%s\" WHERE \"%s\" = ?" % (
                    table_name, key_name),
                value_tuple).fetchall()
        else:
            print("DELETE FROM \"%s\" WHERE \"%s\" IN " % (
                table_name, key_name) + value_tuple.__str__())
            content = conn.execute(
                "DELETE FROM \"%s\" WHERE \"%s\" IN " % (
                    table_name, key_name) + value_tuple.__str__()).fetchall()
        conn.commit()
        conn.close()


def sqlite_select_by_a_key(db_file, table_name, key_name, value_tuple):
    conn = sqlite3.connect(db_file)
    if len(value_tuple) == 0:
        content = conn.execute(
            "SELECT * FROM %s" % table_name).fetchall()
    elif len(value_tuple) == 1:
        content = conn.execute(
            "SELECT * FROM %s WHERE \"%s\" = ?" % (table_name, key_name), value_tuple).fetchall()
    else:
        content = conn.execute(
            "SELECT * FROM %s WHERE \"%s\" IN " % (table_name, key_name) + value_tuple.__str__()).fetchall()
    conn.close()
    return content


def sqlite_select(db_file, table_name, column_list=None, key_name=None, value_tuple=None):
    if column_list is None:
        column_string = "*"
    else:
        column_string = ""
        for i in column_list:
            column_string = column_string + i + ","
        column_string = column_string.rstrip(",")

    if key_name is None:
        conn = sqlite3.connect(db_file)
        # print("SELECT %s FROM %s" % (column_string, table_name))
        content = conn.execute("SELECT %s FROM \"%s\"" %
                               (column_string, table_name)).fetchall()
        conn.close()
        return content
    else:
        conn = sqlite3.connect(db_file)
        value_tuple = tuple(value_tuple)
        if len(value_tuple) == 1:
            content = conn.execute(
                "SELECT %s FROM \"%s\" WHERE \"%s\" = ?" % (
                    column_string, table_name, key_name),
                value_tuple).fetchall()
        else:
            content = conn.execute(
                "SELECT %s FROM \"%s\" WHERE \"%s\" IN " % (
                    column_string, table_name, key_name) + value_tuple.__str__()).fetchall()
        conn.close()
        return content


def sqlite_execute(cmd_string, db_file, commit=False):
    conn = sqlite3.connect(db_file)
    content = conn.execute(cmd_string).fetchall()
    if commit:
        conn.commit()
    conn.close()
    return content


def build_database(data_generator, parse_function, table_columns_dict, sql3_db_file):
    import time
    from toolbiox.lib.xuyuxing.base.common_command import log_print
    from collections import OrderedDict

    start_time = time.time()
    init_sql_db_many_table(sql3_db_file, table_columns_dict)

    record_dict = OrderedDict()
    num = 0
    for record in data_generator:
        record_dict[num] = parse_function(record)
        num += 1

        if len(record_dict) % 10000 == 0:
            for table_name in table_columns_dict:
                record_tuple_now = [record_dict[i][table_name] for i in record_dict]
                sqlite_write(record_tuple_now, sql3_db_file, table_name, table_columns_dict[table_name])
            record_dict = OrderedDict()
        
        round_time = time.time()
        if round_time - start_time > 10:
            log_print("%d finished" % (num))
            start_time = round_time

    if len(record_dict) > 0:
        for table_name in table_columns_dict:
            record_tuple_now = [record_dict[i][table_name] for i in record_dict]
            sqlite_write(record_tuple_now, sql3_db_file, table_name, table_columns_dict[table_name])

    record_dict = OrderedDict()
    log_print("%d finished" % (num))

    return sql3_db_file

# sqlite + pickle


def pickle_dump_obj(unpickled_obj):
    pickled = codecs.encode(pickle.dumps(unpickled_obj), "base64").decode()
    return pickled


def pickle_load_obj(pickled_string):
    unpickled_obj = pickle.loads(
        codecs.decode(pickled_string.encode(), "base64"))
    return unpickled_obj


if __name__ == '__main__':
    db_file = '/lustre/home/xuyuxing/Work/Gel/Gene_Loss/plant/all_map/test/Cau/test.db'

    init_sql_db(db_file, 'table1', ['name', 'sex', 'age'], True)

    record_list = [
        ("Mark Arnold", "M", "28"),
        ("Barbara Jackson", "W", "29"),
        ("Wilhelm Schacht", "M", "")
    ]

    sqlite_write(record_list, db_file, 'table1', ['name', 'sex', 'age'])

    sqlite_update(db_file, 'table1', 'name', 'age', [
                  ("Wilhelm Schacht", 50), ("Mark Arnold", 29)])

    sqlite_delete(db_file, 'table1', 'name',
                  ("Mark Arnold", "Barbara Jackson"))

    # for load a big database into a sqlite
    from Bio import SeqIO
    xml_file = "/lustre/home/xuyuxing/Database/Uniprot/sport/uniprot_sprot.xml"
    sql3_db_file = "/lustre/home/xuyuxing/Database/Uniprot/sport/uniprot_sprot.db"

    table_columns_dict = {'table_record':['id', 'codenstring']}

    data_generator = SeqIO.parse(xml_file, "uniprot-xml")

    def parse_function(seqio_obj):
        return {'table_record': (seqio_obj.id, pickle_dump_obj(seqio_obj))} 

    build_database(data_generator, parse_function, table_columns_dict, sql3_db_file)

    build_index(sql3_db_file, 'table_record', 'id')