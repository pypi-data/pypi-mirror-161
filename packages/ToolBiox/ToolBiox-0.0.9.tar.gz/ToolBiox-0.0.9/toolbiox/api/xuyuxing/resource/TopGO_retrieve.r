# usage: Rscript TopGO.r FG_gene_list.txt BG_GO_base.txt output.txt BP

args<-commandArgs(T)
GOIDFile<-args[1]
FGGeneIDFile<-args[2]
BGmapFile<-args[3]
OutPutFile<-args[4]
Ontology<-args[5]

# GOIDFile<-"/tmp/b30d41ae78ed11ecb43a246e96971c44.go.id"
# FGGeneIDFile<-"/tmp/b30d41ae78ed11ecb43a246e96971c44.id"
# BGmapFile<-"/tmp/b30d41ae78ed11ecb43a246e96971c44.go.base"
# OutPutFile<-"/tmp/b30d41ae78ed11ecb43a246e96971c44.go.out"
# Ontology<-"BP"

library(topGO)
geneID2GO <- readMappings(file = BGmapFile)
GO2geneID <- inverseList(geneID2GO)
geneNames <- names(geneID2GO)

myInterestingGenes=as.character(read.table(FGGeneIDFile)$V1)
geneList <- factor(as.integer(geneNames %in% myInterestingGenes))
names(geneList) <- geneNames

GOdata <- new("topGOdata", ontology = Ontology, allGenes = geneList, annot = annFUN.gene2GO, gene2GO = geneID2GO)
allGO = genesInTerm(GOdata)

myInterestingGO=as.character(read.table(GOIDFile)$V1)

for (go_id in myInterestingGO) {
    for (g_id in allGO[go_id][[go_id]]) {
        # print(c(go_id, g_id))
        cat(paste(go_id,g_id),file=OutPutFile,sep="\n",append=TRUE)
    }
}

