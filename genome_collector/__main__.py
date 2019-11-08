"""Command line to download genomes and build BLAST DBs for Genome Collector.

Usage:
  python -m genome_collector data <taxid> <data_type> [data_dir]
  python -m genome_collector blast_db <taxid> <db_type> [data_dir]

Parameters:
  - taxid: a taxonomic ID. Must have a single reference assembly on NCBI.
  - data_type: one of genomic_fasta, genomic_genbank, genomic_bff,
    protein_fasta.
  - db_type: either "nucl" or "prot".
  - data_dir: optional directory where the data will be downloaded.
"""

import sys
from .GenomeCollection import GenomeCollection

if __name__ == "__main__":
    command = sys.argv[1]
    if command == "data":
        taxid = sys.argv[2]
        data_type = sys.argv[3]
        collection = GenomeCollection()
        if len(sys.argv) == 5:
            collection.data_dir = sys.argv[4]
        collection.download_taxid_genome_data_from_ncbi(
            taxid, data_type=data_type
        )
    elif command == "blast_db":
        collection = GenomeCollection()
        if len(sys.argv) == 5:
            collection.data_dir = sys.argv[4]
        taxid, db_type = sys.argv[2], sys.argv[3]
        collection.generate_blast_db_for_taxid(taxid, db_type=db_type)
    else:
        raise ValueError("Unknown genome_collector command %s." % command)
