"""Mixin for Bowtie methods, inherited by GenomeCollection."""

import time
import random
from urllib import request
from Bio import Entrez
import shutil
import json
import gzip
import os


class NCBIMixin:

    use_ncbi_ftp_via_https = True
    time_between_entrez_requests = 0.34

    def _get_data_from_entrez(self, request, **kwargs):

        # Set the ENTREZ email (mandatory) if not done already

        if Entrez.email is None:
            random_id = random.randint(0, 10000)
            Entrez.email = "genome_collector_%s@replaceme.org" % random_id

        # Be nice to NCBI and wait a bit if the previous request is too recent

        now = time.time()
        last_time = self._time_of_last_entrez_call
        if last_time is not None:
            elapsed = now - last_time
            sleep_time = self.time_between_entrez_requests - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._time_of_last_entrez_call = time.time()

        # Do the request

        search = request(**kwargs)
        return Entrez.read(search)

    def _get_taxid_genome_id_from_ncbi(self, taxid):
        """Return a Genome ID for this TaxID, provided by the NCBI API."""
        taxid = str(taxid)
        data = self._get_data_from_entrez(
            Entrez.esearch, term="txid" + taxid, db="genome", retmode="xml"
        )
        ids = data["IdList"]
        if len(ids) != 1:
            raise IOError(
                "Found %d results (instead of 1) for taxID %s"
                % (len(ids), taxid)
            )
        return ids[0]

    def download_taxid_genome_infos_from_ncbi(self, taxid, assembly_id=None):
        """Download infos on the TaxID and store them in '[taxid].json'.
        
        For taxIDs with several genomes listed on NCBI, you can provide an
        assembly_id, which can also be of the form "#1" to select the first
        available NCBI Assembly ID (first in numerical order).
        """
        taxid = str(taxid)
        self._log_message("Downloading infos for taxid %s from NCBI" % taxid)

        # First get the corresponding genome ID, check that there is only one
        genome_id = self._get_taxid_genome_id_from_ncbi(taxid)

        # Then search for the reference genome, check that there is only one
        results = self._get_data_from_entrez(
            Entrez.esummary, id=genome_id, db="genome", retmode="xml"
        )
        if len(results) != 1:
            raise IOError(
                "Found %d results (instead of 1) for genome %s"
                % (len(results), genome_id)
            )
        infos = dict(**results[0])

        # So far so good, valid TaxID! Let us get more infos about that taxID
        # such as the scientific name, division, etc.
        results = self._get_data_from_entrez(
            Entrez.esummary, id=taxid, db="taxonomy", retmode="xml"
        )
        infos.update(dict(**results[0]))
        infos["taxID"] = taxid
        infos["genomeID"] = genome_id
        if infos["AssemblyID"] == "0":
            data = self._get_data_from_entrez(
                Entrez.esearch,
                term="txid" + taxid,
                db="assembly",
                retmode="xml",
            )
            assembly_ids = data["IdList"]
            if assembly_id is None:
                message = "No AssemblyID found for taxID %s! " % taxid
                if len(assembly_ids) == 0:
                    message += (
                        "And no assembly came up from the NCBI search. Sorry! "
                    )
                else:
                    message += (
                        "You will need to download the infos manually using "
                        "collection.download_taxid_genome_infos_from_ncbi("
                        "taxid, assembly_id=XXX) where assembly_id can be an "
                        "ID, or an index of the form '#1' to select the first "
                        "available assembly_id."
                    )
                raise OSError(message)

            if assembly_id.startswith("#"):
                data = self._get_data_from_entrez(
                    Entrez.esearch,
                    term="txid" + taxid,
                    db="assembly",
                    retmode="xml",
                )
                assembly_ids = data["IdList"]
                if len(assembly_ids) == 0:
                    raise OSError(
                        "Couldn't find an AssemblyID for this genome."
                    )
                assembly_ids = sorted([int(i) for i in assembly_ids])
                assembly_index = int(assembly_id.strip("#"))
                infos["AssemblyID"] = str(assembly_ids[assembly_index])
            else:
                if assembly_id not in assembly_ids:
                    raise ValueError(
                        "NCBI says that %s is not an assembly ID for taxID %s."
                        % (assembly_id, taxid)
                    )
                infos["AssemblyID"] = assembly_id

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
        self._log_message(
            "Getting assembly URL for taxid %s from NCBI" % taxid
        )
        genome_infos = self.get_taxid_infos(taxid)
        assembly_id = genome_infos["AssemblyID"]
        data = self._get_data_from_entrez(
            Entrez.esummary, id=assembly_id, db="assembly", retmode="xml"
        )
        ftp_data = data["DocumentSummarySet"]["DocumentSummary"][0]
        ftp_path = ftp_data["FtpPath_RefSeq"]
        if ftp_path == "":
            ftp_path = ftp_data["FtpPath_GenBank"]

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
        target_data_file = self.datafile_path(taxid, data_type)
        query = "TaxID %s %s" % (data_type, taxid)
        self._log_message("Getting NCBI URL for %s." % query)
        taxid = str(taxid)
        ftp_url = self._get_taxid_assembly_url_from_ncbi(
            taxid, data_type=data_type
        )

        target_gz_file = self.datafile_path(taxid, "%s_gz" % data_type)

        self._log_message("Downloading %s." % query)
        try:
            request.urlretrieve(ftp_url, target_gz_file)
        except request.HTTPError as err:
            raise IOError(
                "NCBI genome URL %s for taxID %s not found: %s"
                % (ftp_url, taxid, err)
            )
        self._log_message("Unzipping  %s." % query)
        with open(target_data_file, "wb") as f_fasta:
            with gzip.open(target_gz_file, "rb") as f_gz:
                shutil.copyfileobj(f_gz, f_fasta)
        self._log_message("Done downloading %s." % query)
