library(WGCNA)

options(stringsAsFactors = FALSE)


args<-commandArgs(T)
inputFile <- args[1]

# inputFile <- "/lustre/home/xuyuxing/Work/Orobanchaceae/Trans/clean_data/Oro/Gene.TMM.matrix"

inputMat <- read.table(inputFile, sep='\t', row.names=1, header=T, 
                     quote="", comment="", check.names=F)

inputMat[inputMat < 2] <- 0
inputMat <- log2(inputMat+1)

dim(inputMat)
names(inputMat)

dataExpr = t(inputMat)

gsg = goodSamplesGenes(dataExpr, verbose = 3)
gsg$allOK

if (!gsg$allOK)
{
  # Optionally, print the gene and sample names that were removed:
  if (sum(!gsg$goodGenes)>0)
     printFlush(paste("Removing genes:", paste(names(dataExpr)[!gsg$goodGenes], collapse = ", ")));
  if (sum(!gsg$goodSamples)>0)
     printFlush(paste("Removing samples:", paste(rownames(dataExpr)[!gsg$goodSamples], collapse = ", ")));
  # Remove the offending genes and samples from the data:
  dataExpr = dataExpr[gsg$goodSamples, gsg$goodGenes]
}

nGenes = ncol(dataExpr)
nSamples = nrow(dataExpr)

sampleTree = hclust(dist(dataExpr), method = "average")

pdf(file = "sampleClustering.pdf", width = 12, height = 9)
par(cex = 0.6)
par(mar = c(0,4,2,0))
plot(sampleTree, main = "Sample clustering to detect outliers", sub="", xlab="", cex.lab = 1.5,
    cex.axis = 1.5, cex.main = 2)
dev.off()

enableWGCNAThreads()

powers = c(c(1:10), seq(from = 12, to=20, by=2))
sft = pickSoftThreshold(dataExpr, powerVector = powers, verbose = 5)

pdf(file = "SoftThreshold.pdf", width = 12, height = 9)
par(mfrow = c(1,2))
cex1 = 0.9
plot(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
     xlab="Soft Threshold (power)",ylab="Scale Free Topology Model Fit,signed R^2",type="n",
     main = paste("Scale independence"));
text(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
     labels=powers,cex=cex1,col="red");
abline(h=0.90,col="red")

plot(sft$fitIndices[,1], sft$fitIndices[,5],
     xlab="Soft Threshold (power)",ylab="Mean Connectivity", type="n",
     main = paste("Mean connectivity"))

text(sft$fitIndices[,1], sft$fitIndices[,5], labels=powers, cex=cex1,col="red")     
dev.off()

power = sft$powerEstimate

type = "unsigned"
if (is.na(power)){
  power = ifelse(nSamples<20, ifelse(type == "unsigned", 9, 18),
          ifelse(nSamples<30, ifelse(type == "unsigned", 8, 16),
          ifelse(nSamples<40, ifelse(type == "unsigned", 7, 14),
          ifelse(type == "unsigned", 6, 12))       
          )
          )
}

# 借助图判断适合的power

if (power < 6){
   power = 9
}

print(power)

net = blockwiseModules(dataExpr, power = power,
                     TOMType = "unsigned", minModuleSize = 30,
                     reassignThreshold = 0, mergeCutHeight = 0.25,
                     numericLabels = TRUE, pamRespectsDendro = FALSE,
                     saveTOMs = TRUE,
                     saveTOMFileBase = "OroTOM", verbose = 3)

table(net$colors)

pdf(file = "moduleColor.pdf", width = 12, height = 9)                     
mergedColors = labels2colors(net$colors)
plotDendroAndColors(net$dendrograms[[1]], mergedColors[net$blockGenes[[1]]],
                  "Module colors",
                  dendroLabels = FALSE, hang = 0.03,
                  addGuide = TRUE, guideHang = 0.05)
dev.off()

moduleLabels = net$colors
moduleColors = labels2colors(net$colors)
MEs = net$MEs;
geneTree = net$dendrograms[[1]];                  

write.csv(moduleLabels, file="moduleLabels.csv")
