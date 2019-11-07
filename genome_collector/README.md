# How it works

The main mechanism of ``genome_collector`` is that data files are always
downloaded as needed and in the same order:

```
infos.yaml => genome.fa => blast_database.nsq
```

For instance, when running ``collection.get_taxid_blastdb_path(12345, 'nucl')``, the
program will first look for a BLAST file of the form ``12345_nucl.nsq``. If none
is found, it will automatically create the blast database using the local genome
``12345.fa``. But what if this file is missing? In that case, it will read the
infos file ``12345.yaml`` (or create it by downloading data from NCBI if needed)
and use the infos to download the genome and create ``12345.fa``. Then it will
create the database, and return the path.