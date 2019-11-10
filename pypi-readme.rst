Genome Collector
================

.. image:: https://travis-ci.org/Edinburgh-Genome-Foundry/genome_collector.svg?branch=master
   :target: https://travis-ci.org/Edinburgh-Genome-Foundry/genome_collector
   :alt: Travis CI build status

.. image:: https://coveralls.io/repos/github/Edinburgh-Genome-Foundry/genome_collector/badge.svg?branch=master
   :target: https://coveralls.io/github/Edinburgh-Genome-Foundry/genome_collector?branch=master


Genome Collector is a Python library to download and manage reference genome
data for specific TaxIDs, in particular nucleotide and protein sequences (in
fasta/genbank/gff formats), and alignment databases (BLAST, Bowtie1/2).

The data is downloaded automatically on a need-to basis, making it very easy
for Python projects to use and re-use reference genomes of E. coli,
S. cerevisiae, and so on, without the worry of manually downloading from NCBI.

Examples
--------

Let's get Biopython records of all protein sequences in E. coli:

.. code:: python

    from genome_collector import GenomeCollection
    collection = GenomeCollection()
    records = collection.get_taxid_biopython_records(511145, "protein_fasta")

And that's it! If the protein data wasn't already on your machine, Genome
Collector downloaded from NCBI, and stored in your "collection" for the next
time time you need it.

Now let's get a path to a local BLAST database for S. cerevisiae:

.. code:: python

    from genome_collector import GenomeCollection
    collection = GenomeCollection()
    db_path = collection.get_taxid_blastdb_path(taxid=559292, db_type='nucl')

If there was no cerevisiae database on your machine, Genome Collector
downloaded the genome data and built it. It is now in your collection, and you
can use the returned ``db_path`` to start a BLAST process:

.. code:: python

    import subprocess
    process = subprocess.run([
        'blastn', '-db', db_path, '-query', 'queries.fa', '-out', 'results.txt'
    ])

Infos
-----

- **Installation:** with ``pip install genome_collector``. Some BLAST and Bowtie
  features also require specific software installed, see docs.

- **Docs**: https://edinburgh-genome-foundry.github.io/genome_collector/

- **Github repo:** released on Github `<https://github.com/Edinburgh-Genome-Foundry/genome_collector>`_

- **Licence:** MIT

- **Similar software:** see pre-existing projects `ncbi-genome-download <https://github.com/kblin/ncbi-genome-download>`_
and `Genomepy <https://github.com/simonvh/genomepy>`_ . In comparison, Genome
Collector is more opinionated, it uses TaxID first and has features like
on-demand genome downloading and database building, and Biopython records loading.


Everyone is welcome to contribute !

More biology software
---------------------

.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Edinburgh-Genome-Foundry.github.io/master/static/imgs/logos/egf-codon-horizontal.png
  :target: https://edinburgh-genome-foundry.github.io/

Genome Collector is part of the
`EGF Codons <https://edinburgh-genome-foundry.github.io/>`_
synthetic biology software suite for DNA design, manufacturing and validation.
