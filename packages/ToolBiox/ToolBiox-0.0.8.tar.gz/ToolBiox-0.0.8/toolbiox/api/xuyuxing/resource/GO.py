"""
obo.py
Provides lightweight parser of OBO ontology files. Uses an in-memory, or
optionally on-disk, SQLite3 db to handle reasoning, and can reason arbitrarily
over given predicate relationships.
"""
import sqlite3
from collections import defaultdict
import networkx as nx
import uuid
import os
from toolbiox.lib.common.os import cmd_run
from collections import OrderedDict
from toolbiox.lib.common.fileIO import tsv_file_dict_parse
#from orderedset import OrderedSet


GRAPH_SCHEMA_SQL = """
CREATE TABLE graph(subject, predicate, object,
    unique(subject, predicate, object) on conflict replace);
"""

INSERT_GRAPH_SQL = """INSERT INTO graph(subject, predicate, object)
VALUES(?, ?, ?)"""

DESC_SQL = """SELECT subject FROM graph WHERE predicate like ?
AND object like ?"""

ASC_SQL = """SELECT object FROM graph WHERE predicate like ?
AND subject like ?"""

MULTIVALUE = ['is_a', 'relationship']

ROOT_NODE = {"GO:0005575":"cellular component", "GO:0003674":"molecular function", "GO:0008150":"biological process"}


def _parse(line):
    """Returns a line split on a ': ' as a key/value."""
    if ':' in line:
        key, val = line.split(': ', 1)
        val = val.strip('\n ')
        return key, val
    else:
        return line, None


def _strip_comments(string):
    """Removes comments (text after ' ! ')."""
    if ' ! ' in string:
        val = string.split('!', 1)
        val = val[0].strip()
        return val
    else:
        return string


def parse_obo(obofile):
    """Yields stanzas as encountered in OBO file as dicts."""
    stanza = None
    kvals = defaultdict(list)

    with open(obofile, 'r') as inf:

        for line in inf:
            if stanza:
                yield stanza
            key, val = _parse(line)
            if val:
                kvals[key].append(_strip_comments(val))
            elif 'id' in kvals:
                for key in kvals:
                    val = kvals[key]
                    kvals[key] = val[0] if (len(val) == 1
                        and key not in MULTIVALUE) else val
                stanza = kvals
                kvals = defaultdict(list)
            else:
                kvals = defaultdict(list)


def _parse_relationship(string):
    """Parses the values from the relationship key.
    Ex: 'part_of GO:0001234 ! some go term' => ('part_of', 'GO:0001234')"""
    string = _strip_comments(string)
    pred, obj = string.split(' ', 1)
    return pred.strip(), obj.strip()


class Obo:
    """Ontology created from an OBO file specified during construction. Use
    Obo.query() to reason over relationships, and Obo.show_relations() to see
    available relationships.
    """
    conn = None
    stanzas = None

    def __init__(self, obofile):
        """Creates a new ontology based off a given OBO file."""
        self._createdb()
        self.stanzas = {}
        
        for stanza in parse_obo(obofile):
            self.stanzas[stanza['id']] = stanza
            self._ins_stanza(stanza)

    def _createdb(self, dbname=':memory:'):
        self.conn = sqlite3.connect(dbname)
        self.conn.execute(GRAPH_SCHEMA_SQL)

    def _ins_stanza(self, stanza):
        if 'is_obsolete' in stanza and stanza['is_obsolete']:
                return
        if 'is_a' in stanza:
            for related in stanza['is_a']:
                self.conn.execute(INSERT_GRAPH_SQL,
                    (stanza['id'], 'is_a', related))
        if 'relationship' in stanza:
            for related in stanza['relationship']:
                relationship, target = _parse_relationship(related)
                self.conn.execute(INSERT_GRAPH_SQL,
                    (stanza['id'], relationship, target))

    def _traverse_tree(self):
        pass

    def get(self, _id):
        return self.stanzas.get(_id, None)

    def find_children(self, _id, expand=False):
        """Returns children (using 'is_a' relation) of given id.
        If expand=True, returns all [great,...] grandchildren."""
        return self.query(_id, 'is_a', expand=expand)

    def find_parents(self, _id, expand=False):
        """Returns parents (using 'is_a' relation) of given id.
        If expand=True, returns all [great,...] grandparents."""
        return self.query(_id, 'is_a', desc=False, expand=expand)

    def most_recent_common_ancestor(self, _id1, _id2, predicate):
        p1 = self.query(_id1, predicate, desc=False, expand=True)
        p2 = self.query(_id2, predicate, desc=False, expand=True)
        for i, path in enumerate(p1):
            pass

    def query(self, _id, predicate, desc=True, expand=False, named=False):
        """Returns all the descendants of a given predicate relationship, or
        if desc=False, returns ascendants. If expand=True, traverses up or
        down graph to terminal nodes."""
        related = []
        sql = DESC_SQL if desc else ASC_SQL
        cur = self.conn.execute(sql, (predicate, _id))
        rset = cur.fetchall()
        cur.close()
        for relative in rset:
            path = []
            path.append((relative[0], self.stanzas[relative[0]]))
            if expand:
                for sub in self.query(relative[0], predicate, desc, expand):
                    path.append((sub[0], self.stanzas[sub[0]]))
            related.extend(path)
        return related

    def relationships(self):
        """Shows all the relationships in the graph."""
        cur = self.conn.execute("select distinct predicate from graph")
        rset = [x[0] for x in cur.fetchall()]
        cur.close()
        return rset

    def get_all_path(self, _id):

        parents_dict = self.find_parents(_id, expand=True)

        all_node_dict = {i[0]:i[1] for i in parents_dict}
        all_node_dict[_id] = self.get(_id)

        edge_list = []
        for go_id in all_node_dict:
            is_a_list = all_node_dict[go_id]['is_a']
            for p_id in is_a_list:
                edge_list.append((go_id,p_id))

        edge_list = list(set(edge_list))

        DG = nx.DiGraph()

        for go_id, p_id in edge_list:
            DG.add_edge(go_id, p_id)

        output_dict = {}
        for target_node in ROOT_NODE:
            output_dict[target_node] = list(nx.all_simple_paths(DG, source=_id, target=target_node))

        return output_dict

def GO_enrichment_by_topGO(foreground_gene_list, background_GO_dict, Ontology='BP'):
    tmp_prefix = "/tmp/" + uuid.uuid1().hex

    foreground_gene_file = tmp_prefix + ".id"
    foreground_gene_list = list(set(foreground_gene_list))
    with open(foreground_gene_file, 'w') as f:
        for i in foreground_gene_list:
            f.write("%s\n" % i)
    
    background_GO_file = tmp_prefix + ".go.base"
    with open(background_GO_file, 'w') as f:
        for i in background_GO_dict:
            background_GO_dict[i] = list(set(background_GO_dict[i]))
            f.write("%s\t%s\n" % (i, ", ".join(background_GO_dict[i])))

    topgo_r_script_file = os.path.split(os.path.realpath(__file__))[0] + "/TopGO.r"
    output_file = tmp_prefix + ".out"

    try:
        cmd_string = "Rscript %s %s %s %s %s" % (topgo_r_script_file, foreground_gene_file, background_GO_file, output_file, Ontology)
        cmd_run(cmd_string, silence=True)

        file_info_dict = tsv_file_dict_parse(output_file, ignore_head_num=1, fieldnames=['Rank', 'GO_id', 'Term', 'Annotated', 'Significant', 'Expected', 'Rank in classic', 'classic', 'KS', 'weight'])

        output_dict = OrderedDict()
        for i in file_info_dict:
            GO_id = file_info_dict[i]['GO_id']
            Rank_in_weight = int(file_info_dict[i]['Rank'])
            Term = file_info_dict[i]['Term']
            Annotated = int(file_info_dict[i]['Annotated'])
            Significant = int(file_info_dict[i]['Significant'])
            Expected = float(file_info_dict[i]['Expected'])
            Rank_in_classic = int(file_info_dict[i]['Rank in classic'])
            if file_info_dict[i]['classic'] == '< 1e-30':
                classic = 1e-35
            else:
                classic = float(file_info_dict[i]['classic'])
            KS = float(file_info_dict[i]['KS'])
            weight = float(file_info_dict[i]['weight'])

            output_dict[GO_id] = {
                "GO_id":GO_id,
                "Rank_in_weight":Rank_in_weight,
                "Term":Term,
                "Annotated":Annotated,
                "Significant":Significant,
                "Expected":Expected,
                "Rank_in_classic":Rank_in_classic,
                "classic":classic,
                "KS":KS,
                "weight":weight,
            }
    except:
        pass

    os.remove(foreground_gene_file)
    os.remove(background_GO_file)
    os.remove(output_file)

    return output_dict

def retrieve_gene_in_GO_by_topGO(GO_list, background_GO_dict, Ontology='BP'):
    tmp_prefix = "/tmp/" + uuid.uuid1().hex

    GO_list_file = tmp_prefix + ".go.id"
    with open(GO_list_file, 'w') as f:
        for i in list(set(GO_list)):
            f.write("%s\n" % i)

    foreground_gene_file = tmp_prefix + ".id"
    foreground_gene_list = list(background_GO_dict.keys())[:5]
    with open(foreground_gene_file, 'w') as f:
        for i in foreground_gene_list:
            f.write("%s\n" % i)
    
    background_GO_file = tmp_prefix + ".go.base"
    with open(background_GO_file, 'w') as f:
        for i in background_GO_dict:
            background_GO_dict[i] = list(set(background_GO_dict[i]))
            f.write("%s\t%s\n" % (i, ", ".join(background_GO_dict[i])))

    topgo_r_retrivere_script_file = os.path.split(os.path.realpath(__file__))[0] + "/TopGO_retrieve.r"
    output_file = tmp_prefix + ".out"

    try:
        cmd_string = "Rscript %s %s %s %s %s %s" % (topgo_r_retrivere_script_file, GO_list_file, foreground_gene_file, background_GO_file, output_file, Ontology)
        cmd_run(cmd_string, silence=True)

        
        file_info_dict = tsv_file_dict_parse(output_file, fieldnames=['go_id', 'g_id'], seq=' ')

        output_dict = {}
        for i in file_info_dict:
            GO_id = file_info_dict[i]['go_id']
            g_id = file_info_dict[i]['g_id']
            
            output_dict.setdefault(GO_id, []).append(g_id)

    except:
        pass

    os.remove(GO_list_file)
    os.remove(foreground_gene_file)
    os.remove(background_GO_file)
    os.remove(output_file)

    return output_dict    

if __name__ == "__main__":

    """
    GO:0005575  cellular component
    GO:0003674  molecular function
    GO:0008150  biological process
    """


    obo_file = "/lustre/home/xuyuxing/Database/GO/go.obo"

    # load file
    ontology = Obo(obo_file)

    # get GO info
    ontology.get("GO:0000002")

    # get children
    ontology.find_children("GO:0000002")

    # get all children
    ontology.find_children("GO:0008150", expand=True)

    # get parents
    ontology.find_parents("GO:0000002")

    # get all parents
    ontology.find_parents("GO:0000012", expand=True)

    # get all path
    list(ontology.get_all_path("GO:0000012"))

    # %%
    # for wangming
    go_id_file = '/lustre/home/xuyuxing/Work/Other/wangming/go.id'

    from toolbiox.lib.common.fileIO import read_list_file
    from toolbiox.lib.common.util import printer_list

    go_id_list = read_list_file(go_id_file)
    # go_id_list = go_id_list[0:5]

    obo_file = "/lustre/home/xuyuxing/Database/GO/go.obo"

    # load file
    ontology = Obo(obo_file)

    with open("/lustre/home/xuyuxing/Work/Other/wangming/go.id.depth", 'w') as f:
        num = 0
        for i in go_id_list:
            num += 1
            print(num)
            try:
                path_dict = ontology.get_all_path(i)
                for root_id in path_dict:
                    depth_list = []
                    if len(path_dict[root_id]) == 0:
                        continue
                    for j in path_dict[root_id]:
                        depth_list.append(len(j) - 1)
                    depth_list = list(set(depth_list))
                    print(i,root_id,depth_list)
                    f.write("%s\t%s\t%s\n" % (i,root_id,printer_list(depth_list,',')))
            except:
                pass
        


