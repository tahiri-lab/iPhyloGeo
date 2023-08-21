# import matplotlib.pyplot as plt

# ctrl+k+u : uncommment, This is a file that calculates the distance between gene sequences in a FASTA file.
# It compares the first sequence with every other sequence using a Blosum matrix. This process can also be performed with amino acid sequences.

# def calculate_similarity_graph(file):
#     blosum_matrix = {
#         'A': {'A': 4, 'C': -2, 'G': 0, 'T': -1},
#         'C': {'A': -2, 'C': 4, 'G': -1, 'T': -2},
#         'G': {'A': 0, 'C': -1, 'G': 4, 'T': -2},
#         'T': {'A': -1, 'C': -2, 'G': -2, 'T': 4}
#     }
#     blosum62_matrix_amino_acid = {
#     'A': {'A':  4, 'R': -1, 'N': -2, 'D': -2, 'C':  0, 'Q': -1, 'E': -1, 'G':  0, 'H': -2, 'I': -1, 'L': -1, 'K': -1, 'M': -1, 'F': -2, 'P': -1, 'S':  1, 'T':  0, 'W': -3, 'Y': -2, 'V':  0, 'B': -2, 'Z': -1, 'X': -1},
#     'R': {'A': -1, 'R':  5, 'N':  0, 'D': -2, 'C': -3, 'Q':  1, 'E':  0, 'G': -2, 'H':  0, 'I': -3, 'L': -2, 'K':  2, 'M': -1, 'F': -3, 'P': -2, 'S': -1, 'T': -1, 'W': -3, 'Y': -2, 'V': -3, 'B': -1, 'Z':  0, 'X': -1},
#     'N': {'A': -2, 'R':  0, 'N':  6, 'D':  1, 'C': -3, 'Q':  0, 'E':  0, 'G':  0, 'H':  1, 'I': -3, 'L': -3, 'K':  0, 'M': -2, 'F': -3, 'P': -2, 'S':  1, 'T':  0, 'W': -4, 'Y': -2, 'V': -3, 'B':  3, 'Z':  0, 'X': -1},
#     'D': {'A': -2, 'R': -2, 'N':  1, 'D':  6, 'C': -3, 'Q':  0, 'E':  2, 'G': -1, 'H': -1, 'I': -3, 'L': -4, 'K': -1, 'M': -3, 'F': -3, 'P': -1, 'S':  0, 'T': -1, 'W': -4, 'Y': -3, 'V': -3, 'B':  4, 'Z':  1, 'X': -1},
#     'C': {'A':  0, 'R': -3, 'N': -3, 'D': -3, 'C':  9, 'Q': -3, 'E': -4, 'G': -3, 'H': -3, 'I': -1, 'L': -1, 'K': -3, 'M': -1, 'F': -2, 'P': -3, 'S': -1, 'T': -1, 'W': -2, 'Y': -2, 'V': -1, 'B': -3, 'Z': -3, 'X': -2},
#     'Q': {'A': -1, 'R':  1, 'N':  0, 'D':  2, 'C': -3, 'Q':  5, 'E':  2, 'G': -2, 'H':  0, 'I': -3, 'L': -2, 'K':  1, 'M':  0, 'F': -3, 'P': -1, 'S':  0, 'T': -1, 'W': -2, 'Y': -1, 'V': -2, 'B':  0, 'Z':  3, 'X': -1},
#     'E': {'A': -1, 'R':  0, 'N':  0, 'D':  2, 'C': -4, 'Q':  2, 'E':  5, 'G': -2, 'H':  0, 'I': -3, 'L': -3, 'K':  1, 'M': -2, 'F': -3, 'P': -1, 'S':  0, 'T': -1, 'W': -3, 'Y': -2, 'V': -2, 'B':  1, 'Z':  4, 'X': -1},
#     'G': {'A':  0, 'R': -2, 'N':  0, 'D': -1, 'C': -3, 'Q': -2, 'E': -2, 'G':  6, 'H': -2, 'I': -4, 'L': -4, 'K': -2, 'M': -3, 'F': -3, 'P': -2, 'S':  0, 'T': -2, 'W': -2, 'Y': -3, 'V': -3, 'B': -1, 'Z': -2, 'X': -1},
#     'H': {'A': -2, 'R':  0, 'N':  1, 'D': -1, 'C': -3, 'Q':  0, 'E':  0, 'G': -2, 'H':  8, 'I': -3, 'L': -3, 'K': -1, 'M': -2, 'F': -1, 'P': -2, 'S': -1, 'T': -2, 'W': -2, 'Y':  2, 'V': -3, 'B':  0, 'Z':  0, 'X': -1},
#     'I': {'A': -1, 'R': -3, 'N': -3, 'D': -3, 'C': -1, 'Q': -3, 'E': -3, 'G': -4, 'H': -3, 'I':  4, 'L':  2, 'K': -3, 'M':  1, 'F':  0, 'P': -3, 'S': -2, 'T': -1, 'W': -3, 'Y': -1, 'V':  3, 'B': -3, 'Z': -3, 'X': -1},
#     'L': {'A': -1, 'R': -2, 'N': -3, 'D': -4, 'C': -1, 'Q': -2, 'E': -3, 'G': -4, 'H': -3, 'I':  2, 'L':  4, 'K': -2, 'M':  2, 'F':  0, 'P': -3, 'S': -2, 'T': -1, 'W': -2, 'Y': -1, 'V':  1, 'B': -4, 'Z': -3, 'X': -1},
#     'K': {'A': -1, 'R':  2, 'N':  0, 'D': -1, 'C': -3, 'Q':  1, 'E':  1, 'G': -2, 'H': -1, 'I': -3, 'L': -2, 'K':  5, 'M': -1, 'F': -3, 'P': -1, 'S':  0, 'T': -1, 'W': -3, 'Y': -2, 'V': -2, 'B':  0, 'Z':  1, 'X': -1},
#     'M': {'A': -1, 'R': -1, 'N': -2, 'D': -3, 'C': -1, 'Q':  0, 'E': -2, 'G': -3, 'H': -2, 'I':  1, 'L':  2, 'K': -1, 'M':  5, 'F':  0, 'P': -2, 'S': -1, 'T': -1, 'W': -1, 'Y': -1, 'V':  1, 'B': -3, 'Z': -1, 'X': -1},
#     'F': {'A': -2, 'R': -3, 'N': -3, 'D': -3, 'C': -2, 'Q': -3, 'E': -3, 'G': -3, 'H': -1, 'I':  0, 'L':  0, 'K': -3, 'M':  0, 'F':  6, 'P': -4, 'S': -2, 'T': -2, 'W':  1, 'Y':  3, 'V': -1, 'B': -3, 'Z': -3, 'X': -1},
#     'P': {'A': -1, 'R': -2, 'N': -2, 'D': -1, 'C': -3, 'Q': -1, 'E': -1, 'G': -2, 'H': -2, 'I': -3, 'L': -3, 'K': -1, 'M': -2, 'F': -4, 'P':  7, 'S': -1, 'T': -1, 'W': -4, 'Y': -3, 'V': -2, 'B': -2, 'Z': -1, 'X': -2},
#     'S': {'A':  1, 'R': -1, 'N':  1, 'D':  0, 'C': -1, 'Q':  0, 'E':  0, 'G':  0, 'H': -1, 'I': -2, 'L': -2, 'K':  0, 'M': -1, 'F': -2, 'P': -1, 'S':  4, 'T':  1, 'W': -3, 'Y': -2, 'V': -2, 'B':  0, 'Z':  0, 'X':  0},
#     'T': {'A':  0, 'R': -1, 'N':  0, 'D': -1, 'C': -1, 'Q': -1, 'E': -1, 'G': -2, 'H': -2, 'I': -1, 'L': -1, 'K': -1, 'M': -1, 'F': -2, 'P': -1, 'S':  1, 'T':  5, 'W': -2, 'Y': -2, 'V':  0, 'B': -1, 'Z': -1, 'X':  0},
#     'W': {'A': -3, 'R': -3, 'N': -4, 'D': -4, 'C': -2, 'Q': -2, 'E': -3, 'G': -2, 'H': -2, 'I': -3, 'L': -2, 'K': -3, 'M': -1, 'F':  1, 'P': -4, 'S': -3, 'T': -2, 'W': 11, 'Y':  2, 'V': -3, 'B': -4, 'Z': -3, 'X': -2},
#     'Y': {'A': -2, 'R': -2, 'N': -2, 'D': -3, 'C': -2, 'Q': -1, 'E': -2, 'G': -3, 'H':  2, 'I': -1, 'L': -1, 'K': -2, 'M': -1, 'F':  3, 'P': -3, 'S': -2, 'T': -2, 'W':  2, 'Y':  7, 'V': -1, 'B': -2, 'Z': -2, 'X': -1},
#     'V': {'A':  0, 'R': -3, 'N': -3, 'D': -3, 'C': -1, 'Q': -2, 'E': -2, 'G': -3, 'H': -3, 'I':  3, 'L':  1, 'K': -2, 'M':  1, 'F': -1, 'P': -2, 'S': -2, 'T':  0, 'W': -3, 'Y': -1, 'V':  4, 'B': -3, 'Z': -2, 'X': -1},
#     'B': {'A': -2, 'R': -1, 'N':  3, 'D':  4, 'C': -3, 'Q':  0, 'E':  1, 'G': -1, 'H':  0, 'I': -3, 'L': -4, 'K':  0, 'M': -3, 'F': -3, 'P': -2, 'S':  0, 'T': -1, 'W': -4, 'Y': -3, 'V': -3, 'B':  4, 'Z':  1, 'X': -1},
#     'Z': {'A': -1, 'R':  0, 'N':  0, 'D':  1, 'C': -3, 'Q':  3, 'E':  4, 'G': -2, 'H':  0, 'I': -3, 'L': -3, 'K':  1, 'M': -1, 'F': -3, 'P': -1, 'S':  0, 'T': -1, 'W': -2, 'Y': -2, 'V': -2, 'B':  1, 'Z':  4, 'X': -1},
#     'X': {'A': -1, 'R': -1, 'N': -1, 'D': -1, 'C': -2, 'Q': -1, 'E': -1, 'G': -1, 'H': -1, 'I': -1, 'L': -1, 'K': -1, 'M': -1, 'F': -1, 'P': -2, 'S':  0, 'T':  0, 'W': -2, 'Y': -1, 'V': -1, 'B': -1, 'Z': -1, 'X': -1}
# }
#     # Define a function to read sequences from a FASTA file
#     def read_fasta(file):
#         sequences = []
#         with open(file, 'r') as f:
#             lines = f.readlines()
#             sequence = ''
#             for line in lines:
#                 if line.startswith('>'):
#                     if sequence:
#                         sequences.append(sequence)
#                         sequence = ''
#                 else:
#                     sequence += line.strip()
#             if sequence:
#                 sequences.append(sequence)
#         return sequences

#     # Read sequences from a FASTA file
#     sequences = read_fasta(file)
#     num_sequences = len(sequences)

#     # Create a range of positions for the nucleotides
#     positions = range(len(sequences[0]))
#     similarity_data = []  # List to store similarity data between sequences

#     # Compare each pair of sequences to calculate similarity
#     for i in range(num_sequences):
#         sequence1 = sequences[i].upper()
#         similarity = []

#         for j in range(i + 1, num_sequences):
#             sequence2 = sequences[j].upper()
#             num_comparisons = min(len(sequence1), len(sequence2))
#             sequence_similarity = []

#             # Compare nucleotides and store their similarity scores
#             for k in range(num_comparisons):
#                 nucleotide1 = sequence1[k]
#                 nucleotide2 = sequence2[k]
#                 sequence_similarity.append(blosum_matrix[nucleotide1][nucleotide2])

#             similarity.append(sequence_similarity)

#         similarity_data.append(similarity)

#     # Create a plot to visualize sequence similarity
#     fig, ax = plt.subplots()
#     line, = ax.plot(positions, similarity_data[0][0], label='Sequence 1 - Sequence 2')
#     ax.set_xlabel('Nucleotide Position')
#     ax.set_ylabel('Similarity')
#     ax.set_title('Similarity between sequences')
#     ax.legend()

#     # Function to update the plotted line with new similarity data
#     def update_line(index):
#         line.set_ydata(similarity_data[index // num_sequences][index % num_sequences])
#         ax.set_title(f'Similarity between sequences {index // num_sequences + 1} - {index % num_sequences + 2}')
#         fig.canvas.draw_idle()

#     # Add previous and next buttons for navigating through sequence pairs
#     axprev = plt.axes([0.81, 0.02, 0.1, 0.04])
#     axnext = plt.axes([0.92, 0.02, 0.1, 0.04])
#     bprev = plt.Button(axprev, 'Previous')
#     bnext = plt.Button(axnext, 'Next')

#     # Class to manage button click events and update the plot
#     class Index:
#         def __init__(self, start, end):
#             self.start = start
#             self.end = end
#             self.current = start

#         def next(self, event):
#             if self.current < self.end:
#                 self.current += 1
#                 update_line(self.current)

#         def prev(self, event):
#             if self.current > self.start:
#                 self.current -= 1
#                 update_line(self.current)

#     # Attach button click events to their respective functions
#     callback = Index(0, num_sequences * (num_sequences - 1) - 1)
#     bprev.on_clicked(callback.prev)
#     bnext.on_clicked(callback.next)

#     # Display the plot
#     plt.show()

#     # Assuming there's a missing function call to 'calculate_similarity_graph'
#     file = 'TAS-42.fasta'
#     calculate_similarity_graph(file)  # This line should be removed or replaced if not needed
