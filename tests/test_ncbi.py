import os
from genome_collector import GenomeCollection
import pytest

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


def test_taxid_with_nonunique_genome(tmpdir):
    taxid = 10710  # LAMBDA PHAGE - has 2 associated assemblies on NCBI
    collection = GenomeCollection(data_dir=str(tmpdir))
    with pytest.raises(OSError) as excinfo:
        path = collection.get_taxid_infos(taxid)
    assert "You will need to download" in str(excinfo.value)
    collection.download_taxid_genome_infos_from_ncbi(taxid, assembly_id="#1")
    path = collection.datafile_path(taxid, data_type="genomic_fasta")
    assert not os.path.exists(path)
    collection.get_taxid_genome_data_path(taxid)
    assert os.path.exists(path)
