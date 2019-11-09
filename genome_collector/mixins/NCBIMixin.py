"""Mixin for Bowtie methods, inherited by GenomeCollection."""

import time
import random
from urllib.request import urlretrieve
from Bio import Entrez
import shutil
import json
import gzip
import os

class NCBIMixin:

    use_ncbi_ftp_via_https = True
    time_between_entrez_requests = 0.34

    def _wait_before_next_entrez_request(self):
        now = time.time()
        last_time = self._time_of_last_entrez_call
        if last_time is not None:
            elapsed = now - last_time
            sleep_time = self.time_between_entrez_requests - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._time_of_last_entrez_call = time.time()

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
        self._wait_before_next_entrez_request()
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

    def download_taxid_genome_infos_from_ncbi(self, taxid):
        """Download infos on the TaxID and store them in '[taxid].json'."""
        taxid = str(taxid)
        self._autoset_entrez_email_if_none()
        self._log_message("Downloading infos for taxid %s from NCBI" % taxid)

        # First get the corresponding genome ID, check that there is only one
        genome_id = self._get_taxid_genome_id_from_ncbi(taxid)

        # Then search for the reference genome, check that there is only one
        self._wait_before_next_entrez_request()
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
        self._wait_before_next_entrez_request()
        search = Entrez.esummary(id=taxid, db="taxonomy", retmode="xml")
        results = Entrez.read(search)
        infos.update(dict(**results[0]))
        infos["taxID"] = taxid
        infos["genomeID"] = genome_id

        # Finally, write the infos locally

        path = self.datafile_path(taxid, data_type="infos")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        with open(path, "w") as f:
            json.dump(infos, f)

    def _get_taxid_assembly_url_from_ncbi(self, taxid, data_type):
        """Return a URL pointing to this taxid's genome sequence in NCBI.
        
        data_type can be either genomic_fasta, protein_fasta, genomic_genbank,
        genomic_gff
        """
        taxid = str(taxid)
        self._autoset_entrez_email_if_none()
        self._log_message(
            "Getting assembly URL for taxid %s from NCBI" % taxid
        )
        genome_infos = self.get_taxid_infos(taxid)
        self._wait_before_next_entrez_request()
        search = Entrez.esummary(
            id=genome_infos["AssemblyID"], db="assembly", retmode="xml"
        )
        data = Entrez.read(search)
        ftp_path = data["DocumentSummarySet"]["DocumentSummary"][0][
            "FtpPath_RefSeq"
        ]
        basename = ftp_path.split("/")[-1]
        if self.use_ncbi_ftp_via_https:
            ftp_path = ftp_path.replace("ftp:", "https:")
        extension = self.datafiles_extensions["%s_gz" % data_type]
        return "/".join([ftp_path, basename + extension])

    def download_taxid_genome_data_from_ncbi(self, taxid, data_type):
        """Download and uncompress a gz file from archives.
        
        data_type is either genomic_fasta, genomic_genbank, genomic_gff,
        or protein_fasta.
        """
        taxid = str(taxid)
        query = "TaxID %s %s" % (data_type, taxid)
        self._log_message("Getting NCBI URL for %s." % query)
        taxid = str(taxid)
        ftp_url = self._get_taxid_assembly_url_from_ncbi(
            taxid, data_type=data_type
        )
        target_gz_file = self.datafile_path(taxid, "%s_gz" % data_type)
        target_data_file = self.datafile_path(taxid, data_type)
        self._log_message("Downloading %s." % query)
        urlretrieve(ftp_url, target_gz_file)
        self._log_message("Unzipping  %s." % query)
        with open(target_data_file, "wb") as f_fasta:
            with gzip.open(target_gz_file, "rb") as f_gz:
                shutil.copyfileobj(f_gz, f_fasta)
        self._log_message("Done downloading %s." % query)