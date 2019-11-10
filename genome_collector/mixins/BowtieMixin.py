"""Mixin for Bowtie methods, inherited by GenomeCollection.""" 

import subprocess
import os

class BowtieMixin:
    """All methods are directly accessible to GenomeCollection instances."""

    def generate_bowtie_index_for_taxid(self, taxid, version="2"):
        """Generate a Bowtie (1 or 2) index for the given TaxID."""
        taxid = str(taxid)
        fa_path = self.get_taxid_genome_data_path(
            taxid, data_type="genomic_fasta"
        )
        db_path = self.datafile_path(
            taxid=taxid, data_type="bowtie%s_index" % version
        )
        bowtie_args = ["bowtie%s-build" % version, fa_path, db_path]

        self._log_message(
            "Generating Bowtie%s index for taxid %s" % (version, taxid)
        )
        pipe = subprocess.PIPE
        process = subprocess.run(bowtie_args, stdout=pipe, stderr=pipe)
        if process.returncode:
            error_message = (
                "Bowtie%s index generation for TaxID %s failed with error: %s"
            ) % (version, taxid, process.stderr)
            raise OSError(error_message)
        self._log_message(
            "Done generating Bowtie%s index for taxid %s" % (version, taxid)
        )

    def get_taxid_bowtie_index_path(self, taxid, version="2"):
        """Get a path to the Bowtie (1 or 2) index for the given TaxID.
        
        This will download data and generate the index if necessary.
        This requires Bowtie (1 or 2) installed.
        """
        taxid = str(taxid)
        index_path = self.datafile_path(
            taxid=taxid, data_type="bowtie%s_index" % version
        )
        expected_file_extension = {"1": ".1.ebwt", "2": ".1.bt2"}
        if not os.path.exists(index_path + expected_file_extension[version]):
            self.generate_bowtie_index_for_taxid(taxid, version=version)
        return index_path
