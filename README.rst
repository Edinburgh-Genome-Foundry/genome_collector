Genome Collector
================
.. image:: https://travis-ci.org/Edinburgh-Genome-Foundry/genome_collector.svg?branch=master
   :target: https://travis-ci.org/Edinburgh-Genome-Foundry/genome_collector
   :alt: Travis CI build status

.. image:: https://coveralls.io/repos/github/Edinburgh-Genome-Foundry/genome_collector/badge.svg?branch=master
   :target: https://coveralls.io/github/Edinburgh-Genome-Foundry/genome_collector?branch=master


Genome Collector (full documentation `here <>`_) is a Python library to
download and store genomes and blast databases for specific TaxIDs. The data
is downloaded automatically and on a need-to basis. This makes it very easy for
Python libraries and web applications to use reference genomes of E. coli,
S. cerevisiae, and so on, without the worry of manually downloading the
genome data.

For instance let's get a path to an E. coli BLAST database:

.. code:: python

    from genome_collector import GenomeCollection
    collection = GenomeCollection()
    db_path = collection.get_taxid_blastdb_path(taxid=511145, db_type='nucl')
    print (db_path)

Result:

.. code::

    [genome_collector] Downloading genome for taxid 511145 from NCBI
    [genome_collector] Getting assembly URL for taxid 511145 from NCBI
    [genome_collector] Downloading infos for taxid 511145 from NCBI
    [genome_collector] Downloading genome FASTA for taxID 511145
    [genome_collector] Now unzipping genome FASTA for taxID 511145.
    [genome_collector] Finished downloading genome for taxID 511145
    [genome_collector] Generating nucl BLAST DB for taxid 511145
    [genome_collector] Done generating nucl BLAST DB for taxid 511145
    /home/USER/.local/share/genome_collector/511145_nucl


What happened: Genome Collector first created a path to your local
nucleotide BLAST database, then noticed that the BLAST database was not already
available on the machine at this path, so it downloaded the genome data and built the
BLAST database to make sure that the returned path actually points to a database
(this is a one-off download which won't happen again as long as the files stay
there).

You can now use the ``db_path`` to start a BLAST process:

.. code:: python

    import subprocess
    process = subprocess.run([
        'blastn', '-db', db_path, '-query', 'queries.fa', '-out', 'results.txt'
    ])


For convenience you can also BLAST in a single command, which will automatically
create the path to the database, and even create the BLAST database from scratch
if the data files aren't there:

.. code:: python

    collection.blast_against_taxid('511145', 'nucl', [
        'blastn', '-query', 'blast_test.fa', "-out", 'result.txt'
    ])


Usage tips
==========

Changing data storage directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can decide where a collection's local files will be stored with the
``data_dir`` parameter of ``GenomeCollection``. Note that the default value for
``data_dir`` is highly recommended as it always points to the same local user
data folder. As a consequence, all librairies and applications using the default
will be able to pick genomes from the same folder. The path of this default
folder, stored at ``collection.data_dir``, is platform-specific:

- ``~/.local/share/genome_collector`` on Linux
- ``~/Library/Application Support/genome_collector`` on MacOS
- ``C:\Documents and Settings\<User>\Application Data\Local Settings\EGF\genome_collector`` on Windows

You can set the local default path globally at the beginning of your Python
script with:

.. code:: python

    from genome_collector import GenomeCollection
    GenomeCollection.default_dir = '/my/new/dir'

Finally, you can set a default path as an environment variable (so it will be
shared by different Python processes):

.. code::

    env GENOME_COLLECTOR_DATA_DIR = /my/other/path



Preventing auto-download
~~~~~~~~~~~~~~~~~~~~~~~~

When using Genome Collector in a particular project, for instance a web app,
you may want to pre-download only a few genomes, and prevent users from using
other genomes. This can be done by setting a collection's ``autodownload``
attribute to False. To globally prevent Genome Collector from downloadind
data files, set this attribute at class level:

.. code:: python

    GenomeCollection.autodownload = False


Command line interface
~~~~~~~~~~~~~~~~~~~~~~

The very basic command-line interface enables to use Genome Collector to
pre-download genomes and pre-build BLAST databases on a machine. This can
be particularly useful in Dockerfiles to set up docker containers.

.. code::

    python -m genome_collector genome 511145
    python -m genome_collector blast_db 511145 nucl


By default these genomes will be downloaded to the platform-specific local
data folder. This can be changed by adding a data_dir at the end:

.. code::

    python -m genome_collector genome 511145 /path/to/some/dir/

Or by setting an environment variable before running these commands:

.. code::

    env GENOME_COLLECTOR_DATA_DIR = /my/other/path


Installation
-------------

You can install genome_collector through PIP

.. code::

    sudo pip install genome_collector

Alternatively, you can unzip the sources in a folder and type

.. code::

    sudo python setup.py install
  
For the BLAST-related features to work, you must have the NCBI BLAST software
installed. For instance on Ubuntu install with:
::
    sudo apt-get install ncbi-blast+

License = MIT
--------------

genome_collector is an open-source software originally written at the
`Edinburgh Genome Foundry <http://genomefoundry.org>`_ by
`Zulko <https://github.com/Zulko>`_ and
`released on Github <https://github.com/Edinburgh-Genome-Foundry/genome_collector>`_
under the MIT licence (copyright Edinburgh Genome Foundry).

Everyone is welcome to contribute !

More biology software
---------------------

.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Edinburgh-Genome-Foundry.github.io/master/static/imgs/logos/egf-codon-horizontal.png
  :target: https://edinburgh-genome-foundry.github.io/

genome_collector is part of the `EGF Codons <https://edinburgh-genome-foundry.github.io/>`_ synthetic biology software suite for DNA design, manufacturing and validation.
