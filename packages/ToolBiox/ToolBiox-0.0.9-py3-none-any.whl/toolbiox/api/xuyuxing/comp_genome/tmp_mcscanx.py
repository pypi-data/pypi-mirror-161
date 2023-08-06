import sys
import re
import string
import commands
import pickle
import copy
import itertools
import subprocess


def samtools_to_fasta(range_string,genome_file_name,output_file):
	cmd_string = "samtools faidx "+genome_file_name+" \""+range_string+"\" >> \""+output_file+"\""
	print cmd_string
	p = subprocess.Popen(cmd_string, shell=True, stderr=subprocess.PIPE)
	p.wait()
	returncode = p.poll()
	if returncode == 1:
		subprocess.call("rm "+output_file, shell=True)
		print "error02"
		return "error02"
	else:
		return output_file
def phylogene_tree(seq_file,tag):
	cmd_string = "clustalw -INFILE=\""+seq_file+"\" -ALIGN -OUTPUT=FASTA -OUTFILE=\""+tag+".aln\" -type=protein"
	p = subprocess.Popen(cmd_string, shell=True, stderr=subprocess.PIPE)
	p.wait()
	returncode = p.poll()
	aln_file = tag+".aln"
	if returncode == 1:
		subprocess.call("rm "+aln_file, shell=True)
		print "error03"
		return "error03"
	cmd_string = "trimal -fasta -gappyout -in \""+aln_file+"\" -out \""+aln_file+".trimal\""
	p = subprocess.Popen(cmd_string, shell=True, stderr=subprocess.PIPE)
	p.wait()
	returncode = p.poll()
	trimal_file = aln_file+".trimal"
	if returncode == 1:
		subprocess.call("rm "+trimal_file, shell=True)
		print "error04"
		return "error04"
	cmd_string = "FastTree \""+trimal_file+"\" > \""+trimal_file+".phb\""
	p = subprocess.Popen(cmd_string, shell=True, stderr=subprocess.PIPE)
	p.wait()
	returncode = p.poll()
	phb_file = trimal_file+".phb"
	if returncode == 1:
		subprocess.call("rm "+trimal_file, shell=True)
		print "error05"
		return "error05"
	else:
		print "ML successful"
		return phb_file


def section(list1,list2):
	all = sorted(list(list1+list2))
	deta = all[2]-all[1]+1
	if max(list1)>=min(list2) and max(list2)>=min(list1):
		If_inter = 1	#Yes
	else:
		If_inter = 0	#No
	return int(If_inter),int(deta)


def hash_map(dict_list):
	dict_hash={}
	for i in dict_list:
		for j in dict_list[i]:
			if not dict_hash.has_key(j):
				dict_hash[j]=[]
			dict_hash[j].append(i)
	return dict_hash
def integrate_element(dict_list,num):
	dict_hash = hash_map(dict_list)
	flag = 0
	deleted=[]
	for i in dict_hash:
		if not len(dict_hash[i]) > 1:
			continue
		dict_list[num]=[]
		for j in dict_hash[i]:
			if j in deleted:
				continue
			dict_list[num]=list(set(dict_list[num]+dict_list[j]))
			del dict_list[j]
			deleted.append(j)
			flag=1
		num=num+1
		break
	return flag,num
def NoRed_element(list_all):
	dict_list={}
	num=0
	for i in list_all:
		dict_list[num]=i
		num=num+1
	#print dict_list
	flag = 1
	while flag == 1:
		flag,num = integrate_element(dict_list,num)
		print len(dict_list)
	output=[]
	for i in dict_list:
		output.append(dict_list[i])
	return output


def Parse_collinearity(mcscanx_collinearity_file):
	F2 = open(mcscanx_collinearity_file)
	colline_block={}
	block_id_dict={}
	for each_line in F2:
		if re.match(r'^#',each_line):
			match = re.match(r'## Alignment .* .* .* .* (\S\S)(.*)\&(\S\S)(.*) .*',each_line)
			if match:
				speci1=match.group(1)
				speci1_contig = match.group(2)
				speci2=match.group(3)
				speci2_contig = match.group(4)
				continue
			else:
				continue
		each_line = re.sub('\n','',each_line)
		info = string.split(each_line,"\t")
		info[0]=re.sub(' ','',info[0])
		block_id,pair_id=string.split(info[0],"-")
		pair_id = re.sub(':','',pair_id)
		
		speci_tag=tuple(sorted([speci1,speci2]))
		if not colline_block.has_key(speci_tag):
			colline_block[speci_tag]={}
		
		if not colline_block[speci_tag].has_key(block_id):
			colline_block[speci_tag][block_id]=[[],[]]
		
		if speci1 == speci2:
			colline_block[speci_tag][block_id][0].append(info[1])
			colline_block[speci_tag][block_id][1].append(info[2])
		elif speci_tag[0]==speci1:					  
			colline_block[speci_tag][block_id][0].append(info[1])
			colline_block[speci_tag][block_id][1].append(info[2])
		elif speci_tag[0]==speci2:					  
			colline_block[speci_tag][block_id][0].append(info[2])
			colline_block[speci_tag][block_id][1].append(info[1])
		
		block_id_dict[block_id]={}
		block_id_dict[block_id]['speci_tag']=speci_tag
		block_id_dict[block_id]['speci1_contig']=speci1_contig
		block_id_dict[block_id]['speci2_contig']=speci2_contig
	F2.close()
	return colline_block,block_id_dict
	
def Find_self_overlap_block(colline_block):
	colline_block_range={}
	colline_block_range_map={}
	for speci_tag in colline_block:
		colline_block_range[speci_tag]={}
		colline_block_range_map[speci_tag]={}
		colline_block_range_map[speci_tag][0]={}
		colline_block_range_map[speci_tag][1]={}
		for block_id in colline_block[speci_tag]:
			list1=[]
			list2=[]
			for i in range(0,len(colline_block[speci_tag][block_id][0])):
				gene1=colline_block[speci_tag][block_id][0][i]
				gene2=colline_block[speci_tag][block_id][1][i]
				list1=list1+[gene_vs_verything[gene1]['start'],gene_vs_verything[gene1]['end']]
				list2=list2+[gene_vs_verything[gene2]['start'],gene_vs_verything[gene2]['end']]
				min_range1=min(list1)
				max_range1=max(list1)
				min_range2=min(list2)
				max_range2=max(list2)
				speci1_contig=gene_vs_verything[gene1]['contig']
				speci2_contig=gene_vs_verything[gene2]['contig']
				speci1=gene_vs_verything[gene1]['speci']
				speci2=gene_vs_verything[gene2]['speci']
			speci1_contig_range = [min_range1,max_range1]
			speci2_contig_range = [min_range2,max_range2]
			colline_block_range[speci_tag][block_id]=[[speci1,speci1_contig,speci1_contig_range],[speci2,speci2_contig,speci2_contig_range]]
			if not colline_block_range_map[speci_tag][0].has_key(speci1_contig):
				colline_block_range_map[speci_tag][0][speci1_contig]=[]
			if not colline_block_range_map[speci_tag][1].has_key(speci2_contig):
				colline_block_range_map[speci_tag][1][speci2_contig]=[]
			colline_block_range_map[speci_tag][0][speci1_contig].append(block_id)
			colline_block_range_map[speci_tag][1][speci2_contig].append(block_id)
	
	intersection_dict={}
	intersection_dict['same_contig']=[]
	intersection_dict['overlap']=[]
	for speci_tag in colline_block_range_map:
		for contig1 in colline_block_range_map[speci_tag][0]:
			for contig2 in colline_block_range_map[speci_tag][1]:
				list1 = colline_block_range_map[speci_tag][0][contig1]
				list2 = colline_block_range_map[speci_tag][1][contig2]
				intersection = list(set(list1)&set(list2))
				if len(intersection) == 0:
					continue
				intersection_dict['same_contig'].append(intersection)
				for block_id1 in intersection:
					for block_id2 in intersection:
						if block_id1 == block_id2:
							continue
						block_id1_info=colline_block_range[speci_tag][block_id1]
						block_id2_info=colline_block_range[speci_tag][block_id2]
						speci1_flag,useless = section(block_id1_info[0][2],block_id2_info[0][2])
						speci2_flag,useless = section(block_id1_info[1][2],block_id2_info[1][2])
						if speci1_flag and speci2_flag:
							intersection_dict['overlap'].append([block_id1,block_id2])
	intersection_dict['overlap'] = NoRed_element(intersection_dict['overlap'])
	return colline_block_range,colline_block_range_map,intersection_dict


def Find_intra_overlap_block(colline_block_all,colline_block_standard):
	colline_block_all_range,colline_block_all_range_map,intersection_all_dict=Find_self_overlap_block(colline_block_all)
	colline_block_standard_range,colline_block_standard_range_map,intersection_standard_dict=Find_self_overlap_block(colline_block_standard)
	intra_overlap={}
	for speci_tag in colline_block_standard_range_map:
		speci1_intersection=[]
		for speci1_contig in colline_block_standard_range_map[speci_tag][0]:
			for standard_block_id in colline_block_standard_range_map[speci_tag][0][speci1_contig]:
				if not colline_block_all_range_map[speci_tag][0].has_key(speci1_contig):
					#print speci1_contig
					continue
				for all_block_id in colline_block_all_range_map[speci_tag][0][speci1_contig]:
					standard_block_info=colline_block_standard_range[speci_tag][standard_block_id]
					all_block_info=colline_block_all_range[speci_tag][all_block_id]
					speci1_flag,useless = section(standard_block_info[0][2],all_block_info[0][2])
					if speci1_flag:
						speci1_intersection.append((standard_block_id,all_block_id))
		speci2_intersection=[]
		for speci2_contig in colline_block_standard_range_map[speci_tag][1]:
			for standard_block_id in colline_block_standard_range_map[speci_tag][1][speci2_contig]:
				if not colline_block_all_range_map[speci_tag][1].has_key(speci2_contig):
					#print speci2_contig
					continue
				for all_block_id in colline_block_all_range_map[speci_tag][1][speci2_contig]:
					standard_block_info=colline_block_standard_range[speci_tag][standard_block_id]
					all_block_info=colline_block_all_range[speci_tag][all_block_id]
					speci2_flag,useless = section(standard_block_info[1][2],all_block_info[1][2])
					if speci2_flag:
						speci2_intersection.append((standard_block_id,all_block_id))
		intra_overlap[speci_tag]=list(set(speci1_intersection) & set(speci2_intersection))
	return intra_overlap
		
def block_search_range(string_search,colline_block_range,colline_block_range_map):
	#string_search="Cc:chr1:1000-2000"
	matchObj=re.match(r'(.*):(.*):(\d+)-(\d+)',string_search)
	output=[]
	if matchObj:
		speci = matchObj.group(1)
		contig = matchObj.group(2)
		start = int(matchObj.group(3))
		end = int(matchObj.group(4))
		#print speci,contig,start,end
		for speci_tag in colline_block_range_map:
			if not speci in speci_tag:
				continue
			speci_index = speci_tag.index(speci)
			if not colline_block_range_map[speci_tag][speci_index].has_key(contig):
				continue
			for block_id in colline_block_range_map[speci_tag][speci_index][contig]:
				info = colline_block_range[speci_tag][block_id]
				speci_info,speci_contig_info,speci_contig_range = info[speci_index]
		#		print speci,speci_info
		#		print contig,speci_contig_info
				speci_flag,useless = section(speci_contig_range,[start,end])
				if speci_flag:
					output.append(block_id)
		return output
	else:
		print "Bad string_search"
		return
	
def block_search_gene(gene1,gene2,gene_vs_verything,colline_block_range,colline_block_range_map):
	gene1_speci = gene_vs_verything[gene1]['speci']
	gene1_contig = gene_vs_verything[gene1]['contig']
	gene1_start = gene_vs_verything[gene1]['start']
	gene1_end = gene_vs_verything[gene1]['end']
	gene2_speci = gene_vs_verything[gene2]['speci']
	gene2_contig = gene_vs_verything[gene2]['contig']
	gene2_start = gene_vs_verything[gene2]['start']
	gene2_end = gene_vs_verything[gene2]['end']
	
	if not gene1_speci == gene2_speci:
		print "Bad querys"
		return
		
	if not gene1_contig == gene2_contig:
		print "Bad querys"
		return
	
	range_list = [gene1_start,gene1_end,gene2_start,gene2_end]


	string_search = gene1_speci+":"+gene1_contig+":"+str(min(range_list))+"-"+str(max(range_list))
	#print string_search
	output = block_search_range(string_search,colline_block_range,colline_block_range_map)
	return output
	
F2 = open("mcscanx.gff")
gff_speci_vs_contig_vs_gene={}
gene_vs_verything={}
for each_line in F2:
	each_line = re.sub('\n','',each_line)
	info = string.split(each_line,"\t")
	match = re.match(r'(\S\S)(.*)',info[0])
	speci=match.group(1)
	contig=match.group(2)
	gene = info[1]
	start = int(info[2])
	end = int(info[3])
	if not gff_speci_vs_contig_vs_gene.has_key(speci):
		gff_speci_vs_contig_vs_gene[speci]={}
	if not gff_speci_vs_contig_vs_gene[speci].has_key(contig):
		gff_speci_vs_contig_vs_gene[speci][contig]=[]
	gff_speci_vs_contig_vs_gene[speci][contig].append([gene,start,end])
	gene_vs_verything[gene]={}
	gene_vs_verything[gene]['speci']=speci
	gene_vs_verything[gene]['contig']=contig
	gene_vs_verything[gene]['start']=start
	gene_vs_verything[gene]['end']=end
F2.close()




F2 = open("mcscanx.tandem.NoRed")
tandem={}
tandem_map={}
num=0
for each_line in F2:
	each_line = re.sub('\n','',each_line)
	info = string.split(each_line,"\t")
	num=num+1
	tandem[num]=[]
	for i in info:
		tandem[num].append(i)
		tandem_map[i]=num
F2.close()


for speci in gff_speci_vs_contig_vs_gene:
	for contig in gff_speci_vs_contig_vs_gene[speci]:
		gff_speci_vs_contig_vs_gene[speci][contig]=sorted(gff_speci_vs_contig_vs_gene[speci][contig],key=lambda e:e[1],reverse=False)


		
colline_block_all,block_id_dict_all = Parse_collinearity("mcscanx.collinearity")
colline_block_standard,block_id_dict_standard = Parse_collinearity("mcscanxh.collinearity")
Intra_overlap = Find_intra_overlap_block(colline_block_all,colline_block_standard)
colline_block_all_range,colline_block_all_range_map,intersection_all_dict=Find_self_overlap_block(colline_block_all)


saved_all=[]
saved_all_list=[]
for speci_tag in Intra_overlap:
	for rec in Intra_overlap[speci_tag]:
		saved_all.append([rec[1]])
		saved_all_list.append(rec[1])
for group in intersection_all_dict['overlap']:
	for id in group:
		if id in saved_all_list:
			saved_all.append(group)
			
saved_all = NoRed_element(saved_all)
saved_all_map = {}
for group in saved_all:
	for block_id in group:
		saved_all_map[block_id]=saved_all.index(group)


#####################################准备完成
		
Cc_gene_block_saved={}
for gene in gene_vs_verything:	
	if gene_vs_verything[gene]['speci'] == "Cc":
		output = block_search_gene(gene,gene,gene_vs_verything,colline_block_all_range,colline_block_all_range_map)
		Cc_gene_block_saved[gene]=[]
		for block_id in output:
			if not saved_all_map.has_key(block_id):
				continue
			Cc_gene_block_saved[gene].append(saved_all_map[block_id])
		Cc_gene_block_saved[gene]=list(set(Cc_gene_block_saved[gene]))
		temp_list=[]
		for index_saved in Cc_gene_block_saved[gene]:
			temp_list.append(saved_all[index_saved])
		Cc_gene_block_saved[gene] = temp_list


num=0
OUT = open("Cca_gene_block_num","w")
for gene in Cc_gene_block_saved:
	print >> OUT,gene,len(Cc_gene_block_saved[gene])
OUT.close()
		
classic_range={}
for gene in Cc_gene_block_saved:
	score={}
	score[('Ca', 'Cc')]=0
	score[('Cc', 'In')]=0
	for block_id_group in Cc_gene_block_saved[gene]:
		speci_tag=block_id_dict_all[block_id_group[0]]['speci_tag']
		for i in score:
			if speci_tag == i:
				score[speci_tag]=score[speci_tag]+1
	if not classic_range.has_key((score[('Ca', 'Cc')],score[('Cc', 'In')])):
		classic_range[(score[('Ca', 'Cc')],score[('Cc', 'In')])]=[]
	classic_range[(score[('Ca', 'Cc')],score[('Cc', 'In')])].append(gene)
		
classic_range_map={}
for i in classic_range:
	for gene in classic_range[i]:
		classic_range_map[gene]=i
		
Cc_coll_stat={}
for contig_Cc in gff_speci_vs_contig_vs_gene['Cc']:
	Cc_coll_stat[contig_Cc]=[]
	for gene in gff_speci_vs_contig_vs_gene['Cc'][contig_Cc]:
		gene = gene[0]
		Cc_coll_stat[contig_Cc].append([gene,classic_range_map[gene]])
		
num=0
OUT = open("Cc_coll_stat","w")
for contig_Cc in Cc_coll_stat:
	for gene in Cc_coll_stat[contig_Cc]:
		gene,Cc_coll = gene
		print >> OUT,gene,Cc_coll
OUT.close()


Target_contig='chr2'
string_search="Cc:chr2:1-54521787"
all_output = block_search_range(string_search,colline_block_all_range,colline_block_all_range_map)


figure_block_id=[]
for block_id in all_output:
	if block_id in saved_all_list:
		figure_block_id.append(block_id)


		


Big_block=[]
for block_id1 in figure_block_id:
	for block_id2 in figure_block_id:
		if block_id1 == block_id2:
			continue
		speci_tag1 = block_id_dict_all[block_id1]['speci_tag']
		Cc_index1 = speci_tag1.index('Cc')
		speci_tag2 = block_id_dict_all[block_id2]['speci_tag']
		Cc_index2 = speci_tag2.index('Cc')
		block_id1_info=colline_block_all_range[speci_tag1][block_id1]
		block_id2_info=colline_block_all_range[speci_tag2][block_id2]
		Cc_flag,useless = section(block_id1_info[Cc_index1][2],block_id2_info[Cc_index2][2])
		if Cc_flag:
			Big_block.append([block_id1,block_id2])
Big_block = NoRed_element(Big_block)
	
Big_block_dict={}	
for group in Big_block:
	Big_block_dict[Big_block.index(group)]={}
	group_range=[]
	group_speci=[]
	for block_id in group:
		speci_tag = block_id_dict_all[block_id]['speci_tag']
		Cc_index = speci_tag.index('Cc')
		block_id_info=colline_block_all_range[speci_tag][block_id]
		group_range.extend(block_id_info[Cc_index][2])
		group_speci.extend(list(speci_tag))
	group_speci=list(set(group_speci))
	group_range=[min(group_range),max(group_range)]
	Big_block_dict[Big_block.index(group)]['range']=group_range
	Big_block_dict[Big_block.index(group)]['coverage']=max(group_range)-min(group_range)
	Big_block_dict[Big_block.index(group)]['group_speci']=group_speci


a=[9455417,14986889]
b=[]
for start in a:
	for index in Big_block_dict:
		if Big_block_dict[index]['range'][0]==start:
			b.append(index)


OUT = open("figure_link.txt","w")
for index in b:
	group = Big_block[index]
	block_contig=[]
	for block_id in group:
		speci_tag = block_id_dict_all[block_id]['speci_tag']
		colline_block_all
		colline_block_all_range
		colline_block_all_range_map[speci_tag]
		block_contig.append(block_id_dict_all[block_id]['speci_tag'][0]+block_id_dict_all[block_id]['speci1_contig'])
		block_contig.append(block_id_dict_all[block_id]['speci_tag'][1]+block_id_dict_all[block_id]['speci2_contig'])
		[[speci1,speci1_contig,speci1_contig_range],[speci2,speci2_contig,speci2_contig_range]]=colline_block_all_range[speci_tag][block_id]
		print >> OUT,speci1+speci1_contig,speci1_contig_range[0],speci1_contig_range[1],speci2+speci2_contig,speci2_contig_range[0],speci2_contig_range[1]
	block_contig=list(set(block_contig))
OUT.close()




OUT = open("length_ratio","w")		
import math
for speci_tag in colline_block_all_range:
	for block_id in colline_block_all_range[speci_tag]:
		[[speci1,speci1_contig,speci1_contig_range],[speci2,speci2_contig,speci2_contig_range]]=colline_block_all_range[speci_tag][block_id]
		spec1_length = float(speci1_contig_range[1]-speci1_contig_range[0])
		spec2_length = float(speci2_contig_range[1]-speci2_contig_range[0])
		log_ratio = math.log(spec1_length/spec2_length,2)
		print >> OUT,speci_tag,log_ratio
OUT.close()
			
block_contig={}
for index in b:
	group = Big_block[index]
	for block_id in group:
		speci_tag = block_id_dict_all[block_id]['speci_tag']
		[[speci1,speci1_contig,speci1_contig_range],[speci2,speci2_contig,speci2_contig_range]]=colline_block_all_range[speci_tag][block_id]
		if not block_contig.has_key(speci1+speci1_contig):
			block_contig[speci1+speci1_contig]=[]
		block_contig[speci1+speci1_contig]=[min(speci1_contig_range+block_contig[speci1+speci1_contig]),max(speci1_contig_range+block_contig[speci1+speci1_contig])]
		if not block_contig.has_key(speci2+speci2_contig):
			block_contig[speci2+speci2_contig]=[]
		block_contig[speci2+speci2_contig]=[min(speci2_contig_range+block_contig[speci2+speci2_contig]),max(speci2_contig_range+block_contig[speci2+speci2_contig])]


Cc_gene_orthology={}
for gene in gene_vs_verything:	
	if gene_vs_verything[gene]['speci'] == "Cc":
		output = block_search_gene(gene,gene,gene_vs_verything,colline_block_all_range,colline_block_all_range_map)
		Cc_gene_block_saved[gene]=[]
		for block_id in output:
			if not saved_all_map.has_key(block_id):
				continue
			speci_tag = block_id_dict_all[block_id]['speci_tag']
			Cc_index = speci_tag.index('Cc')
			if gene in colline_block_all[speci_tag][block_id][Cc_index]:
				gene_index = colline_block_all[speci_tag][block_id][Cc_index].index(gene)
				if Cc_index == 1:
					ortho_gene = colline_block_all[speci_tag][block_id][0][gene_index]
				else:
					ortho_gene = colline_block_all[speci_tag][block_id][1][gene_index]
				if not Cc_gene_orthology.has_key(gene):
					Cc_gene_orthology[gene]=[]
				Cc_gene_orthology[gene].append(ortho_gene)
				Cc_gene_orthology[gene]=list(set(Cc_gene_orthology[gene]))


Cc_gene_orthology_tree={}
for Cc_gene in Cc_gene_orthology:
	Ca = 0
	In = 0
	for other_gene in Cc_gene_orthology[Cc_gene]:
		if gene_vs_verything[other_gene]['speci'] == 'Ca':
			Ca=Ca+1
		elif gene_vs_verything[other_gene]['speci'] == 'In':
			In=In+1
	if Ca >= 2 and In >= 2:
		Cc_gene_orthology_tree[Cc_gene] = Cc_gene_orthology[Cc_gene]
		Cc_gene_orthology_tree[Cc_gene].append(Cc_gene)
		print Cc_gene_orthology_tree[Cc_gene]


phb_file_dict={}
for Cc_gene in Cc_gene_orthology_tree:
	subprocess.call("rm "+Cc_gene+".faa", shell=True)
	for gene in Cc_gene_orthology_tree[Cc_gene]:
		output_file = samtools_to_fasta(gene,"all.pep.faa",Cc_gene+".faa")
	phb_file = phylogene_tree(output_file,Cc_gene)
	phb_file_dict[Cc_gene]=phb_file


				
				
				
				
all_orthology=[]
for block_id in saved_all_list:
	speci_tag = block_id_dict_all[block_id]['speci_tag']
	for i in range(0,len(colline_block_all[speci_tag][block_id][0])):
		all_orthology.append([colline_block_all[speci_tag][block_id][0][i],colline_block_all[speci_tag][block_id][1][i]])
		
all_orthology=NoRed_element(all_orthology)


OUT = open("all_orthology","w")		
for i in all_orthology:
	printer = ""
	for j in i:
		printer=printer+j+"\t"
	printer = printer.rstrip('\t')
	print >> OUT,printer
OUT.close()
