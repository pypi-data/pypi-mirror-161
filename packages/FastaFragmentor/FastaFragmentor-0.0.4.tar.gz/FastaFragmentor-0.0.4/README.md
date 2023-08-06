# FastaDigest

Code to split a long  fasta sequence into shorter sequences of specified length.

## Installation
### From source
1. Clone this repo
```console
git clone git@gitlab.gwdg.de:mpievolbio-scicomp/FastaDigest
```

2. `cd` into cloned repository
```console
cd FastaDigest
```
3. Install dependencies
```console
pip install -r requirements
```
4. Install FastaDigest
```console
pip install .
```

### From pip
```console
pip install FastaDigest
```

## Usage
`FastaDigest` is intended to be used from the command line:

```console
python -m fasta_digest.digest [-h] [-l LENGTH [-s START] sequence.fasta]
```
`-h` invokes the usage instruction, `-l LENGTH` and the input fasta filename are mandatory, the start position `-s START` is optional. 

## How it works
`FastaDigest` 
1. Parses the input fasta file (generates a biopython `SeqRecord.SeqRecord` object.)
2. Compute pairs of start and end coordinates. The first start coordinate is START, the first end coordinate is START + LENGTH. The corresponding fragment will contain all letters from START through position START + LENGTH - 1. The second start coordinate is START + LENGTH, the second end coordinate is START + 2 LENGTH and so forth. In other words, the start coordinate is *inclusive*, the end coordinate is exclusive. **All coordinates are 0-based**, so the first letter in the sequence has position 0.
3. If at some point, the end coordinate is larger than the length of the input sequence, the sequence is supposed to be circular, i.e. the fragment will contain the end of the sequence and the beginning of the sequence, such that its length is again LENGTH. If LENGTH is not an even divisor of the input sequence's length, the last fragment is of length len(input) % LENGTH .
4. All fragments are converted into biopython `SeqRecord.SeqRecord` objects and written to one .fasta file. The fasta headers are copied from the input file and the start and end coordinate of each fragment with respect to the input sequence is appended to the fasta header.
5. The fragments' start and end coordinates are written on the command line output. 

## Results
After successful completion, `FastaDigest` produces one output file that contains the fragmented fasta sequences. The fasta headers contain the fragment's start and end position with respect to the input file. 

## Test
You may want to test the code by running
```console
cd tests
pytest -v .
```

## Bugs, support, and contributions
Please get in touch by posting a new issue if you found a bug, seek support or wish to contribute to `FastaDigest`.
