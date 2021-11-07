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
width <- as.numeric(args[4])
height <- as.numeric(args[5])
tree_width <- as.numeric(args[6])

# Load progressiveMauve result
bbone <- read_mauve_backbone(
    bbone_file,
    ref=1,
    filter_low=0,
    common_blocks_only=TRUE,
)

# Load newick tree file (Delete node labels)
tree <- read.tree(tree_file)
tree$node.label <- NULL
tree <- newick2phylog(write.tree(tree))

# Setup graphics device driver (PDF or SVG)
ext <- file_ext(plot_file)
if (ext == "pdf") {
    pdf(plot_file, onefile=TRUE, width=width, height=height)
} else if (ext == "svg") {
    svg(plot_file, onefile=TRUE, width=width, height=height)
} else if (ext == "jpg") {
    jpeg(plot_file, width=width, height=height, units="in", res=300)
} else if (ext == "png") {
    png(plot_file, width=width, height=height, units="in", res=300)
}

# Plot genome alignment figure
plot_gene_map(
    dna_segs=bbone$dna_segs,
    comparisons=bbone$comparisons,
    tree=tree,
    tree_width=tree_width,
    dna_seg_labels = names(tree$leaves),
    gene_type="side_blocks",
    xlims = NULL,
    global_color_scheme=c("auto", "auto", "grey", 0.7),
    override_color_schemes=TRUE,
    dna_seg_scale=FALSE,
    scale=TRUE,
)
