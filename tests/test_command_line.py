import os
import sys
import subprocess
from genome_collector import GenomeCollection

PHAGE_TAXID = "697289"


def test_command_line_genome(tmpdir):
    data_dir = str(tmpdir)
    assert len(os.listdir(data_dir)) == 0
    args = [
        sys.executable,
        "-m",
        "genome_collector",
        "data",
        PHAGE_TAXID,
        "genomic_fasta",
        data_dir,
    ]
    GenomeCollection.run_process("test_command_line_genome", args)
    assert len(os.listdir(data_dir)) == 3


def test_command_line_blast_db(tmpdir):
    data_dir = str(tmpdir)
    assert len(os.listdir(data_dir)) == 0

    args = [
        sys.executable,
        "-m",
        "genome_collector",
        "blast_db",
        PHAGE_TAXID,
        "nucl",
        data_dir,
    ]
    GenomeCollection.run_process("test_command_line_blast_db", args)
    assert len(os.listdir(data_dir)) == 6


def test_command_line_bowtie(tmpdir):
    data_dir = str(tmpdir)
    assert len(os.listdir(data_dir)) == 0
    args = [
        sys.executable,
        "-m",
        "genome_collector",
        "bowtie1",
        PHAGE_TAXID,
        data_dir,
    ]
    GenomeCollection.run_process("test_command_line_bowtie", args)
    assert len(os.listdir(data_dir)) == 9
