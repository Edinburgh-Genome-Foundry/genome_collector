import os
import subprocess
import sys
import pytest
from genome_collector import GenomeCollection



def test_get_genome_infos(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))

    def get_name(taxid):
        return collection.get_taxid_infos(taxid)["Organism_Name"]

    assert get_name("511145") == "Escherichia coli"
    assert get_name("559292") == "Saccharomyces cerevisiae"


def test_get_genome(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxid = "511145"
    path = collection.datafile_path(taxid, data_type="genome_fasta")
    assert not os.path.exists(path)
    genome_path = collection.get_taxid_genome_path(taxid)
    assert path == genome_path
    file_size = os.stat(genome_path).st_size
    assert 6_000_000 > file_size > 5_000_000


def test_get_blast_database(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxid = "511145"
    path = collection.datafile_path(taxid, data_type="blast_nucl")
    assert not os.path.exists(path + ".nsq")
    blast_db_path = collection.get_taxid_blastdb_path(taxid, db_type="nucl")
    assert path == blast_db_path
    file_size = os.stat(blast_db_path + ".nsq").st_size
    assert 2_000_000 > file_size > 1_000_000


def test_blast_against_taxid(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    blast_results_file = os.path.join(str(tmpdir), "results.txt")
    queries_file = os.path.join("tests", "queries.fa")
    assert not os.path.exists(blast_results_file)
    collection.blast_against_taxid(
        "511145",
        "nucl",
        ["blastn", "-query", queries_file, "-out", blast_results_file],
    )
    file_size = os.stat(blast_results_file).st_size
    assert 4000 > file_size > 3000


def test_list_taxids(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxids = ["224308", "511145", "559292"]
    found_taxids = collection.list_locally_available_taxids("infos")
    assert len(found_taxids) == 0
    for taxid in taxids:
        collection.get_taxid_infos(taxid)

    found_taxids = collection.list_locally_available_taxids("infos")
    assert found_taxids == taxids

    found_taxids = collection.list_locally_available_taxids("genome_fasta")
    assert len(found_taxids) == 0

    for taxid in taxids[:2]:
        collection.get_taxid_genome_path(taxid)
    found_taxids = collection.list_locally_available_taxids("genome_fasta")
    assert found_taxids == taxids[:2]


def test_delete_all_data_files(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxids = ["224308", "511145", "559292"]
    for taxid in taxids:
        collection.get_taxid_infos(taxid)

    found_taxids = collection.list_locally_available_taxids("infos")
    assert len(found_taxids) == 3
    collection.remove_all_local_data_files()

    found_taxids = collection.list_locally_available_taxids("infos")
    assert len(found_taxids) == 0

def test_autodownload_false(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    collection.autodownload = False

    with pytest.raises(FileNotFoundError) as excinfo:
        collection.get_taxid_infos("224308")
    assert "No infos" in str(excinfo.value)

    with pytest.raises(FileNotFoundError) as excinfo:
        collection.get_taxid_genome_path("224308")
    assert "No genome" in str(excinfo.value)

    

def test_command_line_genome(tmpdir):
    data_dir = str(tmpdir)
    assert len(os.listdir(data_dir)) == 0
    subprocess.run(
        [
            sys.executable,
            "-m",
            "genome_collector",
            "genome",
            "511145",
            data_dir,
        ]
    )
    assert len(os.listdir(data_dir)) == 3


def test_command_line_blast_db(tmpdir):
    data_dir = str(tmpdir)
    assert len(os.listdir(data_dir)) == 0
    subprocess.run(
        [
            sys.executable,
            "-m",
            "genome_collector",
            "blast_db",
            "511145",
            "nucl",
            data_dir,
        ]
    )
    assert len(os.listdir(data_dir)) == 6