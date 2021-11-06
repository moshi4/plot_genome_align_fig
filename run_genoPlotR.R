#!/usr/bin/Rscript
suppressMessages(library(genoPlotR))
suppressMessages(library(ade4))
suppressMessages(library(ape))
suppressMessages(library(tools))

# Get argument values
args <- commandArgs(TRUE)
bbone_file <- args[1]
plot_file <- args[2]
tree_file <- args[3]

# Load progressiveMauve result
bbone <- read_mauve_backbone(
	bbone_file,
    ref=1,
    filter_low=0,
	common_blocks_only=TRUE,
)

# Define plot format (PDF or SVG)
ext <- file_ext(plot_file)
if (ext == "pdf") {
    pdf(plot_file, onefile=TRUE)
} else if (ext == "svg") {
    svg(plot_file, onefile=TRUE)
}

gene_type <- "side_blocks" # arrows

if (is.na(tree_file)) {
    tree = NULL
    labels = NULL
} else {
    tree <- newick2phylog(write.tree(read.tree(tree_file)))
    labels = names(tree$leaves)
}

# treed <- ifelse(missing(tree_file), NULL, newick2phylog(readLines(file(tree_file, "r"), 1)))
# print(tree)

plot_gene_map(
    dna_segs=bbone$dna_segs,
    comparisons=bbone$comparisons,
    tree=tree,
    dna_seg_labels = labels,
    gene_type=gene_type,
    # tree=newick2phylog(readLines(file(tree_file, "r"), 1)),
    arrow_head_len=Inf,
    xlims = NULL,
    global_color_scheme=c("auto", "auto", "grey", 0.5),
    override_color_schemes=TRUE,
    dna_seg_scale=FALSE,
    scale=FALSE,
)
