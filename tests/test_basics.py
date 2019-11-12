import os
import subprocess
from genome_collector import GenomeCollection

PHAGE_TAXID = "697289"

def test_get_biopython_records(tmpdir):
    collection = GenomeCollection(data_dir=str(tmpdir))
    records = collection.get_taxid_biopython_records(PHAGE_TAXID)
    assert len(records) == 1
    assert 168000 < len(records[0]) < 170000

