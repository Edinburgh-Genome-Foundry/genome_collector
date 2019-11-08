import os
import subprocess
import sys
import pytest
from genome_collector import GenomeCollection

PHAGE_TAXID = "697289"


def test_get_genome_infos(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))

    def get_name(taxid):
        return collection.get_taxid_infos(taxid)["Organism_Name"]

    assert get_name("511145") == "Escherichia coli"
    assert get_name("559292") == "Saccharomyces cerevisiae"


def test_get_genome(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxid = PHAGE_TAXID
    path = collection.datafile_path(taxid, data_type="genomic_fasta")
    assert not os.path.exists(path)
    genome_path = collection.get_taxid_genome_data_path(taxid)
    assert path == genome_path
    file_size = os.stat(genome_path).st_size
    assert 200_000 > file_size > 150_000


def test_get_blast_database(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxid = PHAGE_TAXID
    path = collection.datafile_path(taxid, data_type="blast_nucl")
    assert not os.path.exists(path + ".nsq")
    
    # Test nucleotide database
    blast_db_path = collection.get_taxid_blastdb_path(taxid, db_type="nucl")
    assert path == blast_db_path
    file_size = os.stat(blast_db_path + ".nsq").st_size
    assert 50_000 > file_size > 30_000

    # Test protein database
    blast_db_path = collection.get_taxid_blastdb_path(taxid, db_type="prot")
    file_size = os.stat(blast_db_path + ".psq").st_size
    assert 60_000 > file_size > 40_000


def test_blast_against_taxid(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    blast_results_file = os.path.join(str(tmpdir), "results.txt")
    queries_file = os.path.join("tests", "queries.fa")
    assert not os.path.exists(blast_results_file)
    collection.blast_against_taxid(
        PHAGE_TAXID,
        "nucl",
        ["blastn", "-query", queries_file, "-out", blast_results_file],
    )
    file_size = os.stat(blast_results_file).st_size
    assert 1200 > file_size > 800


def test_list_taxids(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    taxids = ["511145", "559292", PHAGE_TAXID]
    found_taxids = collection.list_locally_available_taxids("infos")
    assert len(found_taxids) == 0
    for taxid in taxids:
        collection.get_taxid_infos(taxid)

    found_taxids = collection.list_locally_available_taxids("infos")
    assert found_taxids == taxids

    found_taxids = collection.list_locally_available_taxids("genomic_fasta")
    assert len(found_taxids) == 0

    collection.get_taxid_genome_data_path(PHAGE_TAXID)
    found_taxids = collection.list_locally_available_taxids("genomic_fasta")
    assert found_taxids == [PHAGE_TAXID]

    found_taxids = collection.list_locally_available_taxids_names()
    assert len(found_taxids) == 3

    # For coverage!
    collection.list_locally_available_taxids_names(print_mode=True)


def test_get_various_datatypes(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    for data_type in ["protein_fasta", "genomic_fasta", "genomic_genbank"]:
        path = collection.get_taxid_genome_data_path(
            taxid=PHAGE_TAXID, data_type=data_type
        )
        assert os.path.exists(path)


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
        collection.get_taxid_genome_data_path("224308")
    assert "No genome" in str(excinfo.value)


def test_command_line_genome(tmpdir):
    data_dir = str(tmpdir)
    assert len(os.listdir(data_dir)) == 0
    subprocess.run(
        [
            sys.executable,
            "-m",
            "genome_collector",
            "data",
            PHAGE_TAXID,
            "genomic_fasta",
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
            PHAGE_TAXID,
            "nucl",
            data_dir,
        ]
    )
    assert len(os.listdir(data_dir)) == 6
