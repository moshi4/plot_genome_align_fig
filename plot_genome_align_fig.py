#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess as sp
from glob import glob
from pathlib import Path
from typing import Optional

from Bio import Phylo
from Bio.Phylo.BaseTree import Tree


def main(gbk_dir: Path, outdir: Path, tree_file: Optional[Path]):
    """Main function"""
    # Define IN/OUT contents
    user_gbk_dir = outdir / "user_gbk"
    os.makedirs(user_gbk_dir, exist_ok=True)
    shutil.copytree(gbk_dir, user_gbk_dir, dirs_exist_ok=True)

    mauve_outdir = outdir / "mauve"
    xmfa_file = mauve_outdir / "mauve.xmfa"
    bbone_file = mauve_outdir / "mauve.bbone"
    os.makedirs(mauve_outdir, exist_ok=True)

    svg_plot_file = outdir / "genoPlotR_genome_align.svg"
    pdf_plot_file = outdir / "genoPlotR_genome_align.pdf"

    # Align genome & plot figure
    if tree_file:
        guide_tree_file = outdir / "guide_tree.nwk"
        tree: Tree = Phylo.read(tree_file, "newick")
        leaf_name_list = [node.name for node in tree.get_terminals()]
        gbk_file_list = [
            str(user_gbk_dir / (leaf_name + ".gbk")) for leaf_name in leaf_name_list
        ]
        for cnt, node in enumerate(tree.get_terminals(), 1):
            node.name = f"seq{cnt}"
        Phylo.write(tree, guide_tree_file, "newick")
        # Run progressiveMauve
        mauve_cmd = (
            f"progressiveMauve --output={xmfa_file} "
            + f"--backbone-output={bbone_file} "
            + f"--input-guide-tree={guide_tree_file} "
            + f"{' '.join(gbk_file_list)}"
        )
        sp.run(mauve_cmd, shell=True)
        # Run genoPlotR
        svg_plot_cmd = f"./run_genoPlotR.R {bbone_file} {svg_plot_file} {tree_file}"
        sp.run(svg_plot_cmd, shell=True)
        pdf_plot_cmd = f"./run_genoPlotR.R {bbone_file} {pdf_plot_file} {tree_file}"
        sp.run(pdf_plot_cmd, shell=True)

    else:
        gbk_file_list = glob(str(user_gbk_dir) + "/*.gbk")
        # Run progressiveMauve
        mauve_cmd = (
            f"progressiveMauve --output={xmfa_file} "
            + f"--backbone-output={bbone_file} "
            + f"{' '.join(gbk_file_list)}"
        )
        sp.run(mauve_cmd, shell=True)
        # Run genoPlotR
        svg_plot_cmd = f"./run_genoPlotR.R {bbone_file} {svg_plot_file}"
        sp.run(svg_plot_cmd, shell=True)
        pdf_plot_cmd = f"./run_genoPlotR.R {bbone_file} {pdf_plot_file}"
        sp.run(pdf_plot_cmd, shell=True)


def get_args() -> argparse.Namespace:
    """Get argument values

    Returns:
        argparse.Namespace: Argument values
    """
    parser = argparse.ArgumentParser(
        description="Align genome and plot figure using progressiveMauve & genoPlotR",
    )

    parser.add_argument(
        "-g",
        "--gbk_dir",
        required=True,
        type=Path,
        help="Input genbank files directory (*.gbk)",
        metavar="",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        required=True,
        type=Path,
        help="Output directory",
        metavar="",
    )
    parser.add_argument(
        "-t",
        "--tree",
        type=Path,
        help="Newick species tree file",
        default=None,
        metavar="",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    main(
        args.gbk_dir,
        args.outdir,
        args.tree,
    )
