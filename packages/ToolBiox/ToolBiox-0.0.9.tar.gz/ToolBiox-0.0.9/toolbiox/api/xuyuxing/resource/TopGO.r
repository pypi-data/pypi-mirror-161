# usage: Rscript TopGO.r FG_gene_list.txt BG_GO_base.txt output.txt BP

args<-commandArgs(T)
FGGeneIDFile<-args[1]
BGmapFile<-args[2]
OutPutFile<-args[3]
Ontology<-args[4]

library(topGO)
geneID2GO <- readMappings(file = BGmapFile)
GO2geneID <- inverseList(geneID2GO)
geneNames <- names(geneID2GO)

myInterestingGenes=as.character(read.table(FGGeneIDFile)$V1)
geneList <- factor(as.integer(geneNames %in% myInterestingGenes))
names(geneList) <- geneNames

GOdata <- new("topGOdata", ontology = Ontology, allGenes = geneList, annot = annFUN.gene2GO, gene2GO = geneID2GO)

resultFis <- runTest(GOdata, algorithm = "classic", statistic = "fisher")
weight01.t <- runTest(GOdata, algorithm = "weight01", statistic = "t")
weight01.fisher <- runTest(GOdata, statistic = "fisher")
elim.ks <- runTest(GOdata, algorithm = "elim", statistic = "ks")

allRes <- GenTable(GOdata, classic = resultFis, KS = elim.ks, weight = weight01.fisher, orderBy = "weight", ranksOf = "classic", topNodes = length(score(resultFis)))
write.table(allRes,file = OutPutFile,sep="\t")