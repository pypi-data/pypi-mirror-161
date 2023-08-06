from fileinput import filename
from b2bTools.general.Io import B2bIo


class FastaIO:

	@staticmethod
	def read_fasta_from_file(fileName):

		"""
		Reads a FASTA file

		:param fileName: Path to the FASTA file
		:return: List of (seqId, sequenceString) tuples
		"""

		return B2bIo().readFasta(fileName=fileName)

	def read_fasta_from_string(text):
		"""
		Reads a FASTA from a text string

		:param text: Text in the FASTA format
		:return: List of (seqId, sequenceString) tuples
		"""
		return B2bIo().readFasta(None, fileString=text)

	@staticmethod
	def write_fasta(fastaFileName, sequences):

		"""
		Writes sequences in the FASTA format

		:param fastaFileName: Path to the FASTA file
		:param sequences: List of (seqId, sequenceString) tuples
		:return None
		"""

		return B2bIo().writeFasta(fastaFileName=fastaFileName, sequences=sequences)
