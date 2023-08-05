gene2accession_file = '/lustre/home/xuyuxing/Database/NCBI/gene/2020/gene2accession_copy'

import dask.dataframe as dd

df = dd.read_csv(gene2accession_file, delimiter='\t')