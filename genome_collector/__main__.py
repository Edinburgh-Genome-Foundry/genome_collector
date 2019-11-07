"""Command line to download genomes and build BLAST DBs for Genome Collector.

Usage:
  python -m genome_collector genome <taxid> [data_dir]
  python -m genome_collector blast_db <taxid> <db_type> [data_dir]

Where "db_type" is either "nucl" or "prot".
"data_dir" is the directory where the data will be downloaded. 
"""
import sys
from .GenomeCollection import GenomeCollection

if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'genome':
        collection = GenomeCollection()
        if len(sys.argv) == 4:
            collection.data_dir = sys.argv[3]
        collection.download_taxid_genome_from_ncbi(sys.argv[2])
    elif command == 'blast_db':
        collection = GenomeCollection()
        if len(sys.argv) == 5:
            collection.data_dir = sys.argv[4]
        taxid, db_type = sys.argv[2], sys.argv[3]
        collection.generate_blast_db_for_taxid(taxid, db_type=db_type)
    else:
        raise ValueError("Unknown genome_collector command %s." % command)