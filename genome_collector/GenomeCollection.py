import os
import json

import proglog
from Bio import SeqIO

from .mixins.BlastMixin import BlastMixin
from .mixins.NCBIMixin import NCBIMixin
from .mixins.FileManagerMixin import FileManagerMixin
from .mixins.BowtieMixin import BowtieMixin


class GenomeCollection(BlastMixin, NCBIMixin, FileManagerMixin, BowtieMixin):
    """Collection of local data files including genomes and BLAST databases.

    Parameters
    ==========

    data_dir
      Path to the directory where all genomes informations, sequences and
      blast database will be kept. The default value "local_default" means
      that the system-specific user data directory will be used, so either
      ``~/.local/share/genome_collector`` on Linux, or
      ``~/Library/Application Support/genome_collector`` on MacOS, etc.

    logger
      Logger to which the messages will be sent when downloading files or
      building blast databases. Use "bar" for a default bar logger, None
      for no logging, or any Proglog logger.

    Attributes
    ==========

    autodownload
      When an absent local data file is requested and ``autodownload`` is True,
      the file will be automatically downloaded over the Internet. Otherwise
      a FileNotFoundError is raised. Attribute ``autodownload`` can be set to
      False on a single ``collection`` instance, or at class level with
      ``GenomeCollection.autodownload = False`` to globally prevent Genome
      Collector from downloadind data files.

    default_dir
      Default directory to use when parameter data_dir='default'. This
      attribute allows to set a global default_dir at the beginning of a
      script with ``GlobalCollection.default_dir = '/my/new/dir/'``

    messages_prefix
      Prefix appearing as "[prefix] " in all logging messages.

    datafiles_extensions
      Dictionnary linking data file types to standardized file extensions.

    """

    messages_prefix = "[genome_collector] "

    def __init__(self, data_dir="default", logger="bar"):
        if data_dir == "default":
            data_dir = self.default_dir
        self.data_dir = data_dir
        self._logger = proglog.default_bar_logger(logger)
        self._time_of_last_entrez_call = None

    def _log_message(self, message):
        """Send a message (with prefix) to the logger)"""
        self._logger(message=self.messages_prefix + message)

    def get_taxid_infos(self, taxid):
        """Return a dict with data about the taxid.

        Examples
        ========

        >>> collection.get_taxid_infos(511145)
        >>> {
        >>>      'Organism Name': 'Escherischia Coli', 
        >>>      'DefLine': 'A well-studied enteric bacterium',
        >>>      'Organism_Kingdom': 'Bacteria',
        >>>      'AssemblyID': '1755381',
        >>>      ...
        >>> }



        """
        taxid = str(taxid)
        path = self.datafile_path(taxid=taxid, data_type="infos")
        if not os.path.exists(path):
            if not self.autodownload:
                error_message = (
                    "No infos for taxid %s found locally, and parameter "
                    "autodownload_enabled is set to False in "
                    "genome_collector.settings"
                ) % taxid
                raise FileNotFoundError(error_message)
            self.download_taxid_genome_infos_from_ncbi(taxid)
        with open(path, "r") as f:
            return json.load(f)

    def get_taxid_genome_data_path(self, taxid, data_type="genomic_fasta"):
        """Return a path to the taxid's genome sequence. Download if needed.
        
        ``data_type`` is either genomic_fasta, genomic_genbank, genomic_gff,
        or protein_fasta
        """
        taxid = str(taxid)
        path = self.datafile_path(taxid=taxid, data_type=data_type)
        if not os.path.exists(path):
            if not self.autodownload:
                error_message = (
                    "No genome for taxid %s found locally, and parameter "
                    "autodownload_enabled is set to False in "
                    "genome_collector.settings"
                ) % taxid
                raise FileNotFoundError(error_message)
            self.download_taxid_genome_data_from_ncbi(
                taxid, data_type=data_type
            )
        return path

    def get_taxid_biopython_records(
        self, taxid, source_type="genomic_genbank", as_iterator=False
    ):
        path = self.get_taxid_genome_data_path(taxid, data_type=source_type)
        data_format = source_type.split("_")[1]
        records = SeqIO.parse(path, data_format)
        if as_iterator:
            return records
        else:
            return list(records)
