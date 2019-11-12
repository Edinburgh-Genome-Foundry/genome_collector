import os
from genome_collector import GenomeCollection

PHAGE_TAXID = "697289"

def test_get_bowtie_index(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    path = collection.get_taxid_bowtie_index_path(PHAGE_TAXID, version="2")
    assert os.path.exists(path + '.1.bt2')