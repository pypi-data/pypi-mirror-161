from setuptools import setup

setup(
    name='FastaFragmentor',
    version='0.0.4',
    packages=['fasta_digest',
             ],
    license='MIT',
    description="Split fasta sequences into fragments of given length.",
    install_requires=['biopython'],
)
