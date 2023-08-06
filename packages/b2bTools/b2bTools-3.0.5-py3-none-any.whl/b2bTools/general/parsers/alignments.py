from b2bTools.general.Io import B2bIo


class AlignmentsIO:

	@staticmethod
	def read_alignments(fileName, fileType=None, resetAlignRefSeqID=False, gapCode='-'):
		"""
		Reads an Alignment file detecting the file format

		:param fileName: Path to the file
		:return: List of (seqId, sequenceString) tuples
		"""

		return B2bIo().readAlignments(fileName, fileType=fileType, resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_fasta(fileName, resetAlignRefSeqID=False, gapCode='-'):
		"""
		Reads an Alignment file in FASTA format

		:param fileName: Path to the FASTA file
		:return: List of (seqId, sequenceString) tuples
		"""

		return B2bIo().readAlignments(fileName, fileType="FASTA", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_A3M(fileName, resetAlignRefSeqID=False, gapCode='-'):
		"""
		Reads an Alignment file in A3M format

		:param fileName: Path to the FASTA file
		:return: List of (seqId, sequenceString) tuples
		"""

		return B2bIo().readAlignments(fileName, fileType="A3M", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_blast(fileName, resetAlignRefSeqID=False, gapCode='-'):
		"""
		Reads an Alignment file in FASTA format

		:param fileName: Path to the FASTA file
		:return: List of (seqId, sequenceString) tuples
		"""

		return B2bIo().readAlignments(fileName, fileType="Blast", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_balibase(fileName, resetAlignRefSeqID=False, gapCode='-'):
		return B2bIo().readAlignments(fileName, fileType="BaliBase", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_clustal(fileName, resetAlignRefSeqID=False, gapCode='-'):
		return B2bIo().readAlignments(fileName, fileType="CLUSTAL", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_psi(fileName, resetAlignRefSeqID=False, gapCode='-'):
		return B2bIo().readAlignments(fileName, fileType="PSI", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_phylip(fileName, resetAlignRefSeqID=False, gapCode='-'):
		return B2bIo().readAlignments(fileName, fileType="PHYLIP", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def read_alignments_stockholm(fileName, resetAlignRefSeqID=False, gapCode='-'):
		return B2bIo().readAlignments(fileName, fileType="STOCKHOLM", resetAlignRefSeqID=resetAlignRefSeqID, gapCode=gapCode)

	@staticmethod
	def write_fasta_from_alignment(alignFile, outFastaFile):
		return B2bIo().writeFastaFromAlignment(alignFile, outFastaFile)

	@staticmethod
	def write_fasta_from_seq_alignment_dict(seqAlignments, outFastaFile):
		return B2bIo().writeFastaFromSeqAlignmentDict(seqAlignments, outFastaFile)

	@staticmethod
	def json_preds_to_csv_singleseq(json_data, output_dir='results'):
		"""
		Function to save the predictions in the JSON file to a txt-like file
		:param json_data: Input data in JSON format
		:output_dir: Optional path to the output directory
		"""

		return B2bIo().json_preds_to_csv_singleseq(json_data, output_dir)

	@staticmethod
	def json_preds_to_csv_msa(json_data, file_prefix, output_dir='results'):
		"""
		Function to save the predictions in the CSV file to a txt-like file
		:param json_data: Input data in JSON format
		:output_dir: Optional path to the output directory
		:param file_prefix: The prefix of the output file (<output_dir>/<prefix>_b2btools_preds.txt)
		"""

		return B2bIo().json_preds_to_csv_msa(json_data, id=file_prefix, output_dir=output_dir)
