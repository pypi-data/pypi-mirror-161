from b2bTools.general.Io import B2bIo


class NefIO:
    @staticmethod
    def read_nef_file(fileName):
        """
        :param fileName: Input NEF file path
        :return: File object with info, if read, otherwise None.
        """

        return B2bIo().readNefFile(fileName)

    @staticmethod
    def read_nef_file_sequence_shifts(fileName):
        """
        Note: this reader is limited, as it only handles the sequence and chemical shift information.
        It will need to be extended for other data types, if that should become necessary.

        :param fileName: Input NEF file path
        :return: dictionary with chainCode as key, then a list of sequence codes (pos 0) and a list of and shift information (pos 1)
        """

        return B2bIo().readNefFileSequenceShifts(fileName)
