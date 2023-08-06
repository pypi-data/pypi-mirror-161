#! /usr/bin/env python3

from Bio import Seq, SeqIO, SeqRecord
import argparse
import os

def main(args):

    try:
        with open(args.sequence, 'r') as fh:
            genome = next(SeqIO.parse(fh, 'fasta'))

    except:
        raise IOError("Passed sequence file is not readable or does not exist.")
    # Get edges and fragments.
    edges, digests = digest_genome(genome, args.fragment_length, args.start)

    # Get outfile basename.
    ofname_base = ".".join(os.path.basename(args.sequence).split(".")[:-1])

    # Write records.
    write_records_to_fasta(digests, edges, ofname_base, args.demux)

    # Report number of fragments and edges.
    number_of_fragments = len(digests)
    remainder_length = len(digests[-1].seq)

    print("Fragmentation resulted in {} fragments of length {} and one remainder of length {}".format(
        number_of_fragments,
        args.fragment_length,
        remainder_length
    ))

    print("Fragment edges: ", edges)


def write_records_to_fasta(records, edges, ofname_base, demux=False):
    """ Write passed records to file using the fasta format.

    :param records: The records to write
    :type  records: list [SeqRecord.SecRecord]

    :param edges: The fragment start coordinate with respect to the original unfragmented sequence.
    :type  edges: list [int]

    :param ofname_base: Basename of the fasta file(s) to be written.
    :type  ofname_base: str

    :param demux: Flag indicating whether to write to one multifasta file (demux=False, default) or to multiple fasta files each
    containing one fragment (demux=True).
    :type  demux: bool
    """

    if not demux:
        ofname = ofname_base + ".fragments.fasta"
        with open(ofname, 'w') as fh:
            SeqIO.write(records, fh, 'fasta')

    else:
        for record in records:
            fragment = record.description.split(" ")[-1]
            ofname = ofname_base + '.fragment.{}.fasta'.format(fragment)
            with open(ofname, 'w') as fh:
                SeqIO.write([record], fh, 'fasta')




def genome_slice(genome, start, end):
    """
    Take out a slice from the passed genome sequence between start (inclusive) and end (exclusive).

    :param genome: The source genome sequence record
    :type genome: SeqRecord.SeqRecord

    :param start: Start position of the fragment (inclusive, 0-based indexing)
    :type  start: int

    :param stop: Stop position of the fragment (exclusive, 0-based indexing)
    :type  stop: int

    :return: The requested sequence fragment as a Seq.Seq sequence object.
    :rtype: Seq.Seq
    """

    genome_length = len(genome.seq)

    start = start % genome_length
    end = end % genome_length

    if end < start:
        read = genome[start:] + genome[:end]
    elif end == start:
        return
    else:
        read = genome[start:end]

    return read.seq

def digest_genome(genome, slice_length, start=0):
    """ Fragment a passed (genome) sequence into fragments of length `slice_length` and starting from `start`. The fragmentation
    swirls oround at the end of the sequence and continues up to the start position. The last fragment may be shorter than `length` if
    division `len(genome)/length` has a remainder.
    
    :param genome: The sequence to fragment
    :type genome: SeqRecord.SeqRecord
    
    :param slice_length: The fragment length
    :type  slice_length: int (>0)
    
    :return: The fragment lower edges and the fragments as a list of sequence records.
    :rtype: tuple ([int], [SeqRecord.SeqRecord])
    """

    # Calculate fragment start and stop positions from passed arguments. The % genome.seq length makes
    # the bin edges swirl around to the beginning..
    bin_edges = [(slice_length*i+start) % len(genome.seq) for i in range(len(genome.seq)//slice_length+1)]

    # Include the start position as highest bin edge.
    bin_edges = bin_edges + [bin_edges[0]]

    # Get all fragments.
    reads = [genome_slice(genome,s,e) for s,e in zip(bin_edges[:-1], bin_edges[1:])]

    # If bin edges collapse, sequence is empty and should be excluded.
    reads = [rd for rd in reads if rd is not None]

    # Convert to records. Metadata is copied from the original record and fragment edge positions appended.
    records = [SeqRecord.SeqRecord(dgst,
                                id=genome.id,
                                name=genome.name,
                                description=genome.description+" fragment {}..{}".format(s,e)
                                ) for dgst, (s,e) in zip(reads,
                                                        zip(bin_edges[:-1],
                                                            bin_edges[1:]
                                                            )
                                                        )
            ]

    return bin_edges, records


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""Python utility to split a given fasta sequence into fragments
         of given length starting from a given position. If the last fragment extends beyond the end
         of the sequence, fragmentation continues at the beginning of the sequence up until the start position. In other
         words, the passed sequence is treated as a closed circular sequence. The very last fragment may have a shorter
         length than what was passed depending on whether the fragment length equally divides the sequence length."""
    )

    parser.add_argument('-l', '--length',
                        default=None,
                        required=True,
                        help="The length of the fragments into which the input sequence will be split up.",
                        metavar="LENGTH",
                        type=int,
                        dest='fragment_length',
                        )

    parser.add_argument('-s', '--start',
                        default=0,
                        required=False,
                        help="The start position from which to start the fragmentation. Default 0. NOTE: 0-based indexing throughout.",
                        metavar="POS",
                        type=int,
                        dest='start',
                        )

    parser.add_argument('sequence',
                        default=None,
                        help="The file containing the sequence to fragment (expects fasta format).",
                        metavar="sequence",
                        )

    parser.add_argument('-d', '--demux',
                        help="Demultiplex fragments (write each fragment to its own fasta file). Default: off",
                        action="store_true",
                        )


    args = parser.parse_args()

    main(args)
