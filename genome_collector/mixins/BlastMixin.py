"""Mixin with BLAST methods, inherithed by GenomeCollection."""

import subprocess
import os


class BlastMixin:
    """All methods are directly accessible to GenomeCollection instances."""

    def generate_blast_db_for_taxid(self, taxid, db_type="nucl"):
        """Generates a Blast DB for the TaxID. Autodownload FASTA if needed.

        ``db_type`` is either "nucl" (nucleotides database for blastn, blastx)
        or "prot" (protein database, untested).
        """
        taxid = str(taxid)
        data_type = {"nucl": "genomic_fasta", "prot": "protein_fasta"}[db_type]
        fa_path = self.get_taxid_genome_data_path(taxid, data_type=data_type)
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
        message = "Generating %s BLAST DB for taxid %s" % (db_type, taxid)
        self._log_message(message)
        self.run_process(message, blast_args)
        self._log_message(message + " - Done!")

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
        name = "BLASTing against TaxID %s %s: " % (taxid, db_type)
        return self.run_process(name, blast_args)
