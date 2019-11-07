import shutil
import random
import os
import yaml
import re
import gzip
import subprocess
import appdirs
from urllib.request import urlretrieve


from Bio import Entrez
import proglog

LOCAL_DIR = appdirs.user_data_dir(appname="genome_collector", appauthor="EGF")

class GenomeCollection:
    """Collection of local data files including genomes and BLAST databases.

    To prevent the collection from downloading
    ``GenomeCollection.autodownload = False``

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

    datafiles_extensions = {
        "genome_fasta": ".fa",
        "blast_nucl": "_nucl",
        "blast_prot": "_prot",
        "genome_gz": ".fna.gz",
        "infos": ".yaml",
    }
    autodownload = True
    messages_prefix = "[genome_collector] "
    default_dir = os.environ.get('GENOME_COLLECTOR_DATA_DIR', LOCAL_DIR)

    def __init__(self, data_dir="default", logger="bar"):
        if data_dir == "default":
            data_dir = self.default_dir
        self.data_dir = data_dir
        self._logger = proglog.default_bar_logger(logger)

    def _log_message(self, message):
        """Send a message (with prefix) to the logger)"""
        self._logger(message=self.messages_prefix + message)

    def _autoset_entrez_email_if_none(self):
        """Used in functions using Entrez to autoset the Entrez email (required
        to do Entrez requests)"""
        if Entrez.email is None:
            random_id = random.randint(0, 10000)
            Entrez.email = "genome_collector_%s@replaceme.org" % random_id

    def _get_taxid_genome_id_from_ncbi(self, taxid):
        """Return a Genome ID for this TaxID, provided by the NCBI API."""
        taxid = str(taxid)
        self._autoset_entrez_email_if_none()
        search = Entrez.esearch(
            term="txid" + taxid, db="genome", retmode="xml"
        )
        data = Entrez.read(search)
        ids = data["IdList"]
        if len(ids) != 1:
            raise IOError(
                "Found %d results (instead of 1) for taxID %s"
                % (len(ids), taxid)
            )
        return ids[0]

    def datafile_path(self, taxid, data_type):
        """Return a standardized datafile path for the given TaxID.
        
        Unlike get methods such as ``self.get_taxid_genome_path()``, this
        method only returns the path, and does not check whether the files
        exist locally or not.

        Parameter ``data_type`` should be one of genome_fasta, blast_nucl,
        blast_prot, genome_gz, infos.
        """
        taxid = str(taxid)
        filename = taxid + self.datafiles_extensions[data_type]
        return os.path.join(self.data_dir, filename)

    def download_taxid_genome_infos_from_ncbi(self, taxid):
        """Download infos on the TaxID and store them in '[taxid].yaml'."""
        taxid = str(taxid)
        self._autoset_entrez_email_if_none()
        self._log_message("Downloading infos for taxid %s from NCBI" % taxid)

        # First get the corresponding genome ID, check that there is only one

        genome_id = self._get_taxid_genome_id_from_ncbi(taxid)
        
        # Then search for the reference genome, check that there is only one

        search = Entrez.esummary(id=genome_id, db="genome", retmode="xml")
        results = Entrez.read(search)
        if len(results) != 1:
            raise IOError(
                "Found %d results (instead of 1) for genome %s"
                % (len(results), genome_id)
            )
        infos = dict(**results[0])

        # So far so good, valid TaxID! Let us get more infos about that taxID
        # such as the scientific name, division, etc.

        search = Entrez.esummary(id=taxid, db="taxonomy", retmode="xml")
        results = Entrez.read(search)
        infos.update(dict(**results[0]))
        infos["taxID"] = taxid

        # Finally, write the infos locally

        path = self.datafile_path(taxid, data_type="infos")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        with open(path, "w") as f:
            yaml.dump(infos, f)

    def _get_taxid_assembly_url_from_ncbi(self, taxid):
        """Return a URL pointing to this taxid's genome sequence in NCBI."""
        taxid = str(taxid)
        self._autoset_entrez_email_if_none()
        self._log_message(
            "Getting assembly URL for taxid %s from NCBI" % taxid
        )
        genome_infos = self.get_taxid_infos(taxid)
        search = Entrez.esummary(
            id=genome_infos["AssemblyID"], db="assembly", retmode="xml"
        )
        data = Entrez.read(search)
        ftp_path = data["DocumentSummarySet"]["DocumentSummary"][0][
            "FtpPath_RefSeq"
        ]
        basename = ftp_path.split("/")[-1]
        return "/".join([ftp_path, basename + "_genomic.fna.gz"])

    def download_taxid_genome_from_ncbi(self, taxid):
        taxid = str(taxid)
        self._log_message("Downloading genome for taxid %s from NCBI" % taxid)
        taxid = str(taxid)
        ftp_url = self._get_taxid_assembly_url_from_ncbi(taxid)
        target_gz_file = self.datafile_path(taxid, "genome_gz")
        target_fa_file = self.datafile_path(taxid, "genome_fasta")
        self._log_message("Downloading genome FASTA for taxID %s" % taxid)
        urlretrieve(ftp_url, target_gz_file)
        self._log_message("Now unzipping genome FASTA for taxID %s." % taxid)
        with open(target_fa_file, "wb") as f_fasta:
            with gzip.open(target_gz_file, "rb") as f_gz:
                shutil.copyfileobj(f_gz, f_fasta)
        self._log_message("Finished downloading genome for taxID %s" % taxid)

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
            return yaml.load(f, Loader=yaml.CLoader)

    def get_taxid_genome_path(self, taxid):
        """Return a path to the taxid's genome sequence. Download if needed."""
        taxid = str(taxid)
        path = self.datafile_path(taxid=taxid, data_type="genome_fasta")
        if not os.path.exists(path):
            if not self.autodownload:
                error_message = (
                    "No genome for taxid %s found locally, and parameter "
                    "autodownload_enabled is set to False in "
                    "genome_collector.settings"
                ) % taxid
                raise FileNotFoundError(error_message)
            self.download_taxid_genome_from_ncbi(taxid)
        return path

    def generate_blast_db_for_taxid(self, taxid, db_type="nucl"):
        """Generates a Blast DB for the TaxID. Autodownload FASTA if needed.
        
        ``db_type`` is either "nucl" (nucleotides database for blastn, blastx)
        or "prot" (protein database, untested).
        """
        taxid = str(taxid)
        fa_path = self.get_taxid_genome_path(taxid)  # may autodownload
        db_path = self.datafile_path(taxid=taxid, data_type="blast_" + db_type)
        blast_args = [
            "makeblastdb",
            "-in",
            fa_path,
            "-dbtype",
            db_type,
            "-out",
            db_path,
        ]
        self._log_message(
            "Generating %s BLAST DB for taxid %s" % (db_type, taxid)
        )
        pipe = subprocess.PIPE
        process = subprocess.run(blast_args, stdout=pipe, stderr=pipe)
        if process.returncode:
            error_message = (
                "BLAST database generation for TaxID %s failed with error: %s"
            ) % (taxid, process.stderr)
            raise FileNotFoundError(error_message)
        self._log_message(
            "Done generating %s BLAST DB for taxid %s" % (db_type, taxid)
        )

    def get_taxid_blastdb_path(self, taxid, db_type):
        """Get the path to a local blast DB, download and create one if needed.

        ``db_type`` is either "nucl" (nucleotides database for blastn, blastx)
        or "prot" (protein database, untested).
        """
        taxid = str(taxid)
        db_path = self.datafile_path(taxid=taxid, data_type="blast_" + db_type)
        expected_file_extension = {"nucl": ".nsq", "prot": ".psq"}
        if not os.path.exists(db_path + expected_file_extension[db_type]):
            self.generate_blast_db_for_taxid(taxid, db_type=db_type)
        return db_path

    def blast_against_taxid(self, taxid, db_type, blast_args):
        """Run a BLAST, using a genome_collector database.
        
        Parameters
        ==========

        taxid
          TaxID (int or str) of the reference genome against which the query
          will be blaster. If no database for this taxID is available locally
          it will be downloaded.

        db_type
          Either "nucl" (nucleotides database for blastn, blastx) or "prot"
          (protein database, untested).

        blast_args
          List of NCBI-BLAST arguments, for instance ['blastn', '-query',
          'my_sequences.fa', '-out', 'myresults.xml'].

        Examples
        ========

        >>> blast_against_taxid(taxid, db_type, blast_args)
        
        """
        taxid = str(taxid)
        db_path = self.get_taxid_blastdb_path(taxid=taxid, db_type=db_type)
        blast_args = list(blast_args) + ["-db", db_path]
        pipe = subprocess.PIPE
        process = subprocess.run(blast_args, stdout=pipe, stderr=pipe)
        if process.returncode:
            error_message = (
                "BLAST database generation for TaxID %s failed with error: %s"
            ) % (taxid, process.stderr)
            raise IOError(error_message)
        return process.stdout

    def list_locally_available_taxids(self, data_type="infos"):
        """Return all taxIDs for which there is a local data file of this type.
        
        Parameter ``data_type`` should be one of genome_fasta, blast_nucl,
        blast_prot, genome_gz, infos.
        """
        extension = self.datafiles_extensions[data_type]
        local_files = os.listdir(self.data_dir)
        regexpr = r"(\d+)%s(.|$)" % extension
        available_taxids = []
        for filename in local_files:
            match = re.match(regexpr, filename)
            if match is None:
                continue
            available_taxids.append(match.groups()[0])
        return sorted(list(set(available_taxids)))

    def remove_all_taxid_files(self, taxid):
        """Remove all local data files for this TaxID. Return a names list.
        
        Examples
        ========

        To remove all local data files:

        >>> import genome_collector as gd
        >>> for taxid in gd.list_locally_available_taxids():
        >>>     gd.remove_all_taxid_files(taxid)

        """
        regexpr = r"(\d+)"
        removed_files = []
        local_files = os.listdir(self.data_dir)
        for filename in local_files:
            local_files = os.listdir(self.data_dir)
            match = re.match(regexpr, filename)
            if match is None:
                continue
            file_taxid = match.groups()[0]
            if file_taxid == taxid:
                removed_files.append(filename)
                os.remove(os.path.join(self.data_dir, filename))
        return removed_files
    
    def remove_all_local_data_files(self):
        """Remove all the locally stored data files"""
        for taxid in self.list_locally_available_taxids():
            self.remove_all_taxid_files(taxid)
