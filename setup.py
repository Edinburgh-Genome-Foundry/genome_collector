import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open('genome_collector/version.py').read()) # loads __version__

setup(
    name='genome_collector',
    version=__version__,
    author='Zulko',
    url='https://github.com/Edinburgh-Genome-Foundry/genome_collector',
    description='Easily download and store taxID genomes from NCBI',
    long_description=open('pypi-readme.rst').read(),
    license='MIT',
    keywords="NCBI genomes TaxID BLAST Bowtie",
    packages=find_packages(exclude='docs'),
    install_requires=['appdirs', 'Biopython', 'proglog'])
