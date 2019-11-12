import os
from genome_collector import GenomeCollection
import pytest

PHAGE_TAXID = "697289"


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