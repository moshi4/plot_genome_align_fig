#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess as sp
from pathlib import Path
from typing import List

from Bio import Phylo
from Bio.Phylo.BaseTree import Tree


def main(
    indir: Path,
    outdir: Path,
    tree_file: Path,
    width: int,
    height: int,
    tree_width: int,
):
    """Main function"""
    # Define IN/OUT contents
    genome_dir = outdir / "genome_data"
    mauve_outdir = outdir / "mauve"
    xmfa_file = mauve_outdir / "mauve.xmfa"
    bbone_file = mauve_outdir / "mauve.bbone"
    os.makedirs(genome_dir, exist_ok=True)
    os.makedirs(mauve_outdir, exist_ok=True)
    shutil.copytree(indir, genome_dir, dirs_exist_ok=True)

    # Setup progressiveMauve & genoPlotR input data
    genome_file_list = get_genome_file_list(genome_dir, tree_file)
    guide_tree_file = mauve_outdir / "guide_tree.nwk"
    write_guide_tree(tree_file, guide_tree_file)

    # Run progressiveMauve
    mauve_cmd = (
        f"progressiveMauve --output={xmfa_file} "
        + f"--backbone-output={bbone_file} "
        + f"--input-guide-tree={guide_tree_file} "
        + f"{' '.join(genome_file_list)}"
    )
    if not bbone_file.exists():
        sp.run(mauve_cmd, shell=True)

    # Run genoPlotR
    for ext in (".jpg", ".png", ".svg", ".pdf"):
        plot_file = outdir / ("genoPlotR_genome_align" + ext)
        plot_cmd = (
            f"./run_genoPlotR.R {bbone_file} {plot_file} {tree_file} "
            + f"{width} {height} {tree_width}"
        )
        sp.run(plot_cmd, shell=True)


def get_args() -> argparse.Namespace:
    """Get argument values

    Returns:
        argparse.Namespace: Argument values
    """
    parser = argparse.ArgumentParser(
        description="Align genome and plot figure using progressiveMauve & genoPlotR",
    )

    parser.add_argument(
        "-i",
        "--indir",
        required=True,
        type=Path,
        help="Input genome Genbank or Fasta files directory (*.gbk|*.fa)",
        metavar="I",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        required=True,
        type=Path,
        help="Output directory",
        metavar="O",
    )
    parser.add_argument(
        "-t",
        "--tree",
        required=True,
        type=Path,
        help="Newick species tree file",
        metavar="T",
    )
    default_plot_width = 10
    parser.add_argument(
        "--width",
        type=int,
        default=default_plot_width,
        help=f"Plot width inch (Default: {default_plot_width})",
        metavar="",
    )
    default_plot_height = 7
    parser.add_argument(
        "--height",
        type=int,
        default=default_plot_height,
        help=f"Plot height inch (Default: {default_plot_height})",
        metavar="",
    )
    default_tree_width = 2
    parser.add_argument(
        "--tree_width",
        type=int,
        default=default_tree_width,
        help=f"Plot tree width inch (Default: {default_tree_width})",
        metavar="",
    )

    return parser.parse_args()


def get_genome_file_list(genome_dir: Path, tree_file: Path) -> List[str]:
    """Get genome file list in genome_dir from tree names

    Args:
        genome_dir (Path): Genome genbank or fasta files directory
        tree_file (Path): Newick tree file

    Returns:
        List[str]: Genome genbank or fasta file list
    """
    tree: Tree = Phylo.read(tree_file, "newick")
    leaf_name_list = [node.name for node in tree.get_terminals()]
    genome_file_list = []
    for leaf_name in leaf_name_list:
        file_prefix = genome_dir / leaf_name
        gbk_file = Path(f"{file_prefix}.gbk")
        fasta_file = Path(f"{file_prefix}.fa")
        if gbk_file.exists():
            genome_file_list.append(str(gbk_file))
        elif fasta_file.exists():
            genome_file_list.append(str(fasta_file))
        else:
            err = f"Genome file '{gbk_file}' or '{fasta_file}' not found!!"
            raise FileNotFoundError(err)
    return genome_file_list


def write_guide_tree(tree_file: Path, guide_tree_file: Path) -> None:
    """Write guide tree for progressiveMauve

    Args:
        tree_file (Path): Input newick tree file
        guide_tree_file (Path): Output newick guide tree file
    """
    tree: Tree = Phylo.read(tree_file, "newick")
    for cnt, node in enumerate(tree.get_terminals(), 1):
        node.name = f"seq{cnt}"
    Phylo.write(tree, guide_tree_file, "newick", plain=True)


if __name__ == "__main__":
    args = get_args()
    main(
        args.indir,
        args.outdir,
        args.tree,
        args.width,
        args.height,
        args.tree_width,
    )
