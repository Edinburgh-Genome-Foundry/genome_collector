"""Mixin with everything related to file creation/deletion/listing..."""

import os
import re
import appdirs

LOCAL_DIR = appdirs.user_data_dir(appname="genome_collector", appauthor="EGF")

class FileManagerMixin:
    """All methods are directly accessible to GenomeCollection instances."""

    datafiles_extensions = {
        "genomic_fasta": "_genomic.fa",
        "genomic_genbank": "_genomic.gb",
        "genomic_gff": "_gff.gb",
        "protein_fasta": "_protein.fa",
        "blast_nucl": "_nucl",
        "blast_prot": "_prot",
        "genomic_fasta_gz": "_genomic.fna.gz",
        "genomic_genbank_gz": "_genomic.gbff.gz",
        "genomic_gff_gz": "_genomic.gff.gz",
        "protein_fasta_gz": "_protein.faa.gz",
        "infos": ".json",
        "bowtie1_index": "_bowtie1",
        "bowtie2_index": "_bowtie2",
    }
    autodownload = True
    default_dir = os.environ.get("GENOME_COLLECTOR_DATA_DIR", LOCAL_DIR)

    def datafile_path(self, taxid, data_type):
        """Return a standardized datafile path for the given TaxID.
  
        Unlike get methods such as ``self.get_taxid_genome_data_path()``, this
        method only returns the path, and does not check whether the files
        exist locally or not.

        Parameter ``data_type`` should be one of genomic_fasta, protein_fasta,
        blast_nucl, blast_prot, genomic_gz, protein_gz, infos.
        """
        taxid = str(taxid)
        filename = taxid + self.datafiles_extensions[data_type]
        return os.path.join(self.data_dir, filename)

    def list_locally_available_taxids(self, data_type="infos"):
        """Return all taxIDs for which there is a local data file of this type.

        Parameter ``data_type`` should be one of genomic_fasta, protein_fasta,
        blast_nucl, blast_prot, genomic_gz, protein_gz, infos.
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

    def list_locally_available_taxids_names(self, print_mode=False):
        """Return a dictionnary {taxid: scientific_name} of all local taxIDs.
        
        For convenience, when print_mode is set to True, the table is printed
        in alphabetical order instead of being returned as a dict.
        """
        result = {
            taxid: self.get_taxid_infos(taxid)["ScientificName"]
            for taxid in self.list_locally_available_taxids(data_type="infos")
        }
        if print_mode:
            items = sorted(result.items(), key=lambda item: item[1])
            print("\n".join([taxid.ljust(10) + name for taxid, name in items]))
        else:
            return result

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