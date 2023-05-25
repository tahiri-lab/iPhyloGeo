import os
import subprocess
from io import StringIO
from Bio import SeqIO
from Bio import Entrez
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# ---------------------------------------
# Download sequenceing data from NCBI
# db_type: "nucleotide"; "protein"


def downFromNCBI(db_type, accession_list, file_name):
    Entrez.email = "806981384wl@gmail.com"  # Always tell NCBI who you are

    if not os.path.isfile(file_name):
        # Downloading...
        net_handle = Entrez.efetch(
            db=db_type, id=accession_list, rettype="fasta", retmode="text"
        )
        out_handle = open(file_name, "w")
        out_handle.write(net_handle.read())
        out_handle.close()
        net_handle.close()
        print("Saved")


# file_name = "seq_input.fasta"
# accession_list = ['OP722492', 'OP271297', 'ON763516']

# downFromNCBI("nucleotide", accession_list, file_name)

# file_name = "seq_aa_input.fasta"
# accession_list = ['WAQ35336', 'WAQ35344', 'WAQ35455']

# downFromNCBI("protein", accession_list, file_name)
# ---------------------------------------------------
# Alignment
# in a function. takes unaligned SeqIO object and returns aligned SeqIO object
# (1) convert a SeqIO object to a string then to bytes.
# (2) pass this encoded string to a subprocess call of maft through STDOUT.
# (3) Mafft reads the encoded fasta through STDIN and ouputs the aligned fasta through STDOUT.
#  This STDOUT is then decoded back into a python string and read as a new aligned SeqIO object.


def align_seqs(seqs):
    seq_str = ''
    for seq in seqs:
        seq_str += '>' + seq.id.split('.')[0] + '\n'
        seq_str += str(seq.seq) + '\n'
    child = subprocess.Popen(['mafft', '--quiet', '-'],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    child.stdin.write(seq_str.encode())
    child_out = child.communicate()[0].decode('utf8')
    seq_ali = list(SeqIO.parse(StringIO(child_out), 'fasta'))
    child.stdin.close()
    return seq_ali


def align_withMAFFT(input_fasta, output_fasta):
    # conda install -c bioconda mafft
    seqs = list(SeqIO.parse(input_fasta, 'fasta'))
    seq_ali = align_seqs(seqs)
    with open(output_fasta, "w") as output_handle:
        SeqIO.write(seq_ali, output_handle, "fasta")
