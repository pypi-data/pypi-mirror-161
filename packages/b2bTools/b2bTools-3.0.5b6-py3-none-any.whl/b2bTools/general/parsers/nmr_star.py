from b2bTools.general.Io import B2bIo


class NMRStarIO:
    @staticmethod
    def read_nmr_star_project(fileName):
        """
        :param filenNme:  Input NMR-STAR file path
        :return: file content connected to nmrStarFile object
        """

        return B2bIo().readNmrStarProject(fileName)

    @staticmethod
    def read_nmr_star_sequence_shifts(fileName, original_numbering=True):
        """
        :param fileName: Input NMR-STAR file path
        :param original_numbering: If set to True (Boolean), will retain original sequence code numbering
        :return: dictionary with sequence and shift information
        """

        return B2bIo().readNmrStarSequenceShifts(fileName, original_numbering)