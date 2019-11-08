# This is the basic example of the README to get you started.

from genome_collector import GenomeCollection
import subprocess

# GET A BLAST PATH
collection = GenomeCollection()
db_path = collection.get_taxid_blastdb_path(taxid=511145, db_type="nucl")

process = subprocess.run(
    [
        "blastn",
        "-db",
        db_path,
        "-query",
        "basic_example_queries.fa",
        "-out",
        "basic_example_results.txt",
    ],
    stderr=subprocess.PIPE
)
if process.returncode:
    raise OSError("BLAST failed: %s" % process.stderr)

print("All good! see basic_example_results.txt for results.")