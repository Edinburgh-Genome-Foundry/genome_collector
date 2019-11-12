# Code organization

- **GenomeCollection.py** implements the main class. However, because this class
  has a lot of methods, they have been separated into "mixins" to keep files
  sizes reasonable. Each file in ``mixins/`` implements a set of of methods
  for GenomeCollection around a different theme:
    - **mixins/BlastMixin**: all methods to create BLAST databases and return
      their path.
    - **mixins/BowtieMixin**: all methods to create Bowtie indexes and return
      their path.
    - **mixins/NCBIMixin**: all methods to find the URLs and download infos
      and sequences. 
    - **mixins/FileManagerMixin**: all methods to browse the local data files,
      and delete them if needed.
- **__main__.py** implements the script executed when using Genome Collector
  via the command line (``python -m genome_collector <genome>``).

# How it works

The main mechanism of ``genome_collector`` is that data files are always
downloaded as needed and in the same order:

```
infos.json => genomic.fna.gz => genomic.fa => blast_database.nsq
```

For instance, when running ``collection.get_taxid_blastdb_path(12345, 'nucl')``, the
program will first look for a BLAST file of the form ``12345_nucl.nsq``. If none
is found, it will automatically create the blast database using the local genome
``12345.fa``. But what if this file is missing? In that case, it will read the
infos file ``12345.json`` (or create it by downloading data from NCBI if needed)
and use the infos to download the genome and create ``12345.fa``. Then it will
create the database, and return the path.