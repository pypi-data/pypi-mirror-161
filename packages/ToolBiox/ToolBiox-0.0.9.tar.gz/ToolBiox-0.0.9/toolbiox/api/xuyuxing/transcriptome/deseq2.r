#! /lustre/home/wu_lab/Program/anaconda3/envs/deseq2/bin/Rscript

# usage: Rscript deseq2.xyx.r featureCount.txt coldata.csv

args<-commandArgs(T)

library("BiocParallel")
register(MulticoreParam(4))

# input

print("Reading sample file")
coldata=read.csv(args[2],row.names=1)
print(coldata)


print("Reading count file")
counts=read.csv(args[1], sep="", head=T, skip=1, row.names = "Geneid")
colnames(counts) <- sub(".accepted_hits.bam", "", colnames(counts))
colnames(counts) <- sub(".sort.bam", "", colnames(counts))
colnames(counts) <- sub(".bam", "", colnames(counts))
print(colnames(counts))

counts = counts[,6:length(colnames(counts))]

counts = counts[, rownames(coldata)]

library("DESeq2")

dds <- DESeqDataSetFromMatrix(countData = counts, colData = coldata, design = ~ condition)

# pre-filtering

keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]

# deseq

dds <- DESeq(dds)

tag_list = combn(unique(coldata[,1]),2)

for (i in 1:ncol(tag_list)){
    condition1 = as.character(tag_list[,i][1])
    condition2 = as.character(tag_list[,i][2])
    res <- results(dds, contrast=c("condition",condition1,condition2))
    resOrdered <- res[order(res$pvalue),]

    output_file = paste(condition1,"_vs_",condition2,".deseq2.csv",sep="")

    write.csv(as.data.frame(resOrdered), file=output_file)

    output_plot = paste(condition1,"_vs_",condition2,".plotMA.svg",sep="")
    svg(filename=output_plot)
    plotMA(res, ylim=c(-2,2))
    dev.off()

}


vsd <- vst(dds, blind=FALSE)
write.csv(assay(vsd), file="vsd.csv")

pcaData <- plotPCA(vsd, intgroup=c("condition"), returnData=TRUE)
write.csv(pcaData, file="pca.csv")

percentVar <- round(100 * attr(pcaData, "percentVar"))
write.csv(percentVar, file="pca.contr.csv")

output_plot = paste("pca.svg",sep="")
plotPCA(vsd, intgroup=c("condition"))
dev.off()

