#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Retrieves the taxonomy file listing all organisms and the gene ID to KO mapping
files via the KEGG REST API for all organisms specified in the taxonomy file.
Modules will also be downloaded.
Files are saved as text files within a subdirectory. Existing files will be
overwritten.
Usage: buildKeggDB.py
"""
from toolbiox.api.xuyuxing.resource.kegg.kegg_config import *
import urllib.request
import os
import errno
import sys

def buildModuleList():
    # Prepare download directory. Create directory if it does not exist.
    try:
        os.makedirs(KEGGDIRNAME)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(KEGGDIRNAME):
            raise

    # Download modules files from KEGG and save it.
    urllib.request.urlretrieve('http://rest.kegg.jp/list/module',
                       KEGGDIRNAME + '/ModuleList.txt')

    # Prepare file with modules and names and save it.
    try:
        os.remove(KEGGDIRNAME + '/ModulesNames.txt')
    except OSError:
        pass

    with open(KEGGDIRNAME + '/ModuleList.txt', 'r') as fin, open(
            KEGGDIRNAME + '/ModulesNames.txt', 'a') as fout:
        for line in fin.readlines():
            module = line.split('\t')[0].split(':')[1]
            name = line.split('\t')[1]
            fout.write(module + ': ' + name)

    # Prepare file with modules and save it.
    try:
        os.remove(KEGGDIRNAME + '/Modules.txt')
    except OSError:
        pass

    with open(KEGGDIRNAME + '/ModuleList.txt', 'r') as fin, open(KEGGDIRNAME +
                                                                 '/Modules.txt',
                                                                 'a') as fout:
        for line in fin.readlines():
            module = line.split('\t')[0].split(':')[1]
            fout.write(module + '\n')

def downloadTaxonomy():
    """
    Get taxonomy file with all organism codes from KEGG.
    """
    urllib.request.urlretrieve(TAXURL, KEGGDIRNAME + '/taxonomy.txt')


def buildOrgCodes(groups):
    """
    Save all organism codes in a list.
    Input: List of strings defning the groups for which taxonomy information
    will be downloaded (Prokaryotes, Eukaryotes)
    Output: List of organism codes
    """
    ORG_CODES = []
    TAXONOMY = []
    with open(KEGGDIRNAME + '/taxonomy.txt', 'r') as f:
        TAXONOMY = f.readlines()
    for line in TAXONOMY:
        assert len(line) > 0
        # get only those organisms from groups that are specified (Prokaryotes,
        # and/or Eukaryotes)
        if line.split('\t')[3].split(';')[0] in groups:
            # append the organism code to the list of all organisms of interest
            ORG_CODES.append(line.split('\t')[1])
    return ORG_CODES


def downloadGeneKO(organism):
    """
    Function to download the gene ID to KO mapping file for an organism via
    KEGG REST API.
    Input: string (organism code)
    Output: saved text file
    """
    urllib.request.urlretrieve(KOURL + organism, KEGGDIRNAME + '/' + organism + '.txt')


def downloadGeneEC(organism):
    """
    Function to download the gene ID to EC mapping file for an organism via
    KEGG REST API.
    Input: string (organism code)
    Output: saved text file
    """
    urllib.request.urlretrieve(ECURL + organism, KEGGDIRNAME + '/EC/'
                       + organism + '.txt')

def downloadGenePW(organism):
    """
    Function to download the gene ID to pathway mapping file for an organism via
    KEGG REST API.
    Input: string (organism code)
    Output: saved text file
    """
    urllib.request.urlretrieve(PWURL + organism, KEGGDIRNAME + '/EC/'
                       + organism + '.txt')

def downloadPW(organism):
    """
    Function to download the gene ID to pathway mapping file for an organism via
    KEGG REST API.
    Input: string (organism code)
    Output: saved text file
    """
    urllib.request.urlretrieve(PWURL + organism, KEGGDIRNAME + '/EC/'
                       + organism + '.txt')


# Main
if __name__ == '__main__':

    # ##### CUSTOMIZE #####
    # Directory where all downloaded KEGG data will be stored
    KEGGDIRNAME = '/lustre/home/xuyuxing/Database/kegg'

    # Directory where all downloaded KEGG EC data will be stored
    ECDIRNAME = KEGGDIRNAME + '/EC'

    # Directory where files with gene ID to KO mappings for each sample are stored
    MAPPINGSDIR = KEGGDIRNAME+'/mappings'

    # Directory where files with gene ID to EC mappings for each sample are stored
    ECMAPPINGSDIR = MAPPINGSDIR+'/EC'

    # Directory where module information for each sample is stored
    RESULTSDIR = KEGGDIRNAME+'/results'

    # Directory where EC information for each sample is stored
    ECRESULTSDIR = RESULTSDIR+'/EC'

    # specify Prokaryotes and/or Eukaryotes
    ORGANISMGROUP = ['Eukaryotes']
    # #####

    

    mkdir(KEGGDIRNAME, True)
    # Download taxonomy file
    downloadTaxonomy()
    # Download mapping files for all organisms in the list
    for organism in buildOrgCodes(ORGANISMGROUP):
        downloadGeneKO(organism)

    buildModuleList()