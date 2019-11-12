import os
from genome_collector import GenomeCollection

PHAGE_TAXID = "697289"

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