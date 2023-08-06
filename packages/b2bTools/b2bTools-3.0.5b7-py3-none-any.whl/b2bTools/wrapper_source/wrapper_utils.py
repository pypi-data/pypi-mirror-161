from datetime import timedelta
import time
import numpy as np
from ..singleSeq.Predictor import MineSuite
from ..multipleSeq.msa_core import predManager
from ..multipleSeq.msa_core import BlastManager
from ..multipleSeq.msa_core import MsaManager
from ..multipleSeq.msa_core import UniRef50Manager
from ..general.plotter import Plotter
from ..singleSeq.PSPer.Predictor import PSPer as PspSuite

from ..singleSeq import constants

class SingleSeq:
    """
    Stores the sequences, the filename where they were read from, tools to be executed and the result of the
    predicitons.

    Parameters:

            fileName (str): Path to the fasta file where the sequences of interest are located.
    """

    def __init__(self, fileName):
        """
        Constructor for the SingleSeq class. Reads the fasta file that contains the sequences, calls a function that
        reads the sequences and creates the structure to store all the information required to run and store the
        predicitons.

        Parameters:

            fileName (str): Path to the fasta file where the sequences of interest are located.


        """
        self.__mineSuite__ = MineSuite()
        self.__pspSuite = PspSuite()
        self.__sequenceFileName__ = fileName
        self.__sequences__ = self.__mineSuite__.readFasta(fileName, short_id=False)
        self.__sequences_count__ = len(self.__sequences__)
        self.__predictor_runners__ = {
            constants.TOOL_DYNAMINE: self.__mineSuite__.dynaMine,
            constants.TOOL_DISOMINE: self.__mineSuite__.disoMine,
            constants.TOOL_EFOLDMINE: self.__mineSuite__.eFoldMine,
            constants.TOOL_AGMATA: self.__mineSuite__.agmata,
            constants.TOOL_PSP: self.__pspSuite
        }

        self.__results__ = {}

    def __str__(self):
        return f"Single Sequence Biophysical predictions: input_file={self.__sequenceFileName__}; sequences (count)={len(self.__sequences__)};"


    def __repr__(self):
        return str(self)

    # This method has the responsibility of running the asked predictions in a smart way: it omits the tools that already have a result
    def predict(self, tools=[]):
        """
        This method has the responsibility of running the asked predictions in a smart way: it omits the tools that
        already have a result and runs the remaining.

        Parameters:

            tools (list[str]) : List of tools to be ran. Any combination of the following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"
                - "psp"

        Returns:

            obj: self
        """

        tools = list(set(tools))

        for tool in tools:
            dependencies = constants.DEPENDENCIES[tool]

            if (len(dependencies) > 0):
                self.predict(tools=dependencies)

            if not self.__results__.get(tool):
                start_time = time.process_time()

                predictor_function = self.__predictor_runners__[tool]
                predictor_function.allPredictions = self._all_predictions()

                if tool == constants.TOOL_EFOLDMINE:
                    predictor_function.predictSeqs(self.__sequences__, dynaMinePreds=predictor_function.allPredictions)
                elif tool == constants.TOOL_PSP:
                    seqs_dict = dict((key, value) for key, value in self.__sequences__)
                    predictor_function.predictSeqs(seqs_dict)
                else:
                    predictor_function.predictSeqs(self.__sequences__)

                self.__results__[tool] = predictor_function.allPredictions

                elapsed_time = time.process_time() - start_time
                print(f"Executed {tool.capitalize()}: sequences (count)={self.__sequences_count__}; elapsed time (total)={timedelta(seconds=elapsed_time)}; elapsed time(avg. seq)={timedelta(seconds=elapsed_time/self.__sequences_count__)}")

        return self

    # Instead of using a list of tools as in predict method, this one uses flags to create a list of tools and call
    # the predict method:
    def semantic_predict(
            self,
            dynamics=False,
            aggregation=False,
            early_folding_propensity=False,
            disorder=False,
            phase_separating_protein=False
    ):
        """
        Instead of using a list of tools as in predict method, this one uses flags on the (high level) type of
        predictions desired to create a list of tools and call the predict method.

        Parameters:

            dynamics (bool, optional) : Whether or not dynamics predictions are to be ran
            aggregation (bool, optional) : Whether or not aggregation predictions are to be ran
            early_folding_propensity (bool, optional) : Whether or not early folding propensity predictions are to be ran
            disorder (bool, optional) : Whether or not disorder predictions are to be ran
            phase_separating_protein (bool, optional): Whether or not phase separating protein (PSP) are to be ran

        Returns:

            obj: self
        """
        tools_to_run = []

        if dynamics:
            tools_to_run.append(constants.TOOL_DYNAMINE)
        if aggregation:
            tools_to_run.append(constants.TOOL_AGMATA)
        if early_folding_propensity:
            tools_to_run.append(constants.TOOL_EFOLDMINE)
        if disorder:
            tools_to_run.append(constants.TOOL_DISOMINE)
        if phase_separating_protein:
            tools_to_run.append(constants.TOOL_PSP)

        return self.predict(tools=tools_to_run)

    def explicit_definition_predictions(self, backbone_dynamics=False,
                                        sidechain_dynamics=False,
                                        propoline_II=False,
                                        disorder_propensity=False,
                                        coil=False,
                                        beta_sheet=False,
                                        alpha_helix=False,
                                        early_folding_propensity=False,
                                        aggregation_propensity=False,
                                        protein_score=False,
                                        viterbi=False,
                                        complexity=False,
                                        arg=False,
                                        tyr=False,
                                        RRM=False):


        """

        Instead of using a list of tools as in predict method, this one uses flags on the (explicit) type of
        predictions desired to create a list of tools and call the predict method.

        Parameters:

            backbone_dynamics (bool, optional) : Whether or not backbone dynamics are to be predicted
            sidechain_dynamics (bool, optional) : Whether or not sidechain dynamics are to be predicted
            propoline_II (bool, optional) : Whether or not propoline II propensity is to be predicted
            disorder_propensity (bool, optional) : Whether or not disorder propensity is to be predicted
            coil (bool, optional) : Whether or not coil propensity is to be predicted
            beta_sheet (bool, optional) : Whether or not beta sheet propensity is to be predicted
            alpha_helix (bool, optional) : Whether or not alpha helix propensity is to be predicted
            early_folding_propensity (bool, optional) : Whether or not early folding propensity is to be predicted
            aggregation_propensity (bool, optional) : Whether or not aggregation propensity is to be predicted
            protein_score (bool, optional): Whether or not protein score from PSP is to be predicted
            viterbi (bool, optional): Whether or not Viterbi from PSP is to be predicted
            complexity (bool, optional): Whether or not complexity from PSP is to be predicted
            arg (bool, optional): Whether or not ARG from PSP is to be predicted
            tyr (bool, optional): Whether or not TYR from PSP is to be predicted
            RRM (bool, optional): Whether or not RRM from PSP is to be predicted

        Returns:

            obj: self

        """

        tools_to_run = []

        if backbone_dynamics or sidechain_dynamics or coil or beta_sheet or alpha_helix or propoline_II:
            tools_to_run.append(constants.TOOL_DYNAMINE)
        if disorder_propensity:
            tools_to_run.append(constants.TOOL_DISOMINE)
        if early_folding_propensity:
            tools_to_run.append(constants.TOOL_EFOLDMINE)
        if aggregation_propensity:
            tools_to_run.append(constants.TOOL_AGMATA)
        if protein_score or viterbi or complexity or arg or tyr or RRM:
            tools_to_run.append(constants.TOOL_PSP)

        return self.predict(tools=tools_to_run)

    def _all_predictions(self):
        all_predictions = {}

        for tool in self.__predictor_runners__:
            current_tool_predictions = self.__predictor_runners__[tool].allPredictions
            for sequence_key in current_tool_predictions:
                if not sequence_key in all_predictions:
                    all_predictions[sequence_key] = current_tool_predictions[sequence_key]
                else:
                    all_predictions[sequence_key].update(current_tool_predictions[sequence_key])

        return all_predictions

    def get_all_predictions_json(self, identifier):
        """
        Outputs all available predictions in a JSON formatted string. This still needs to be written in the desired
        output channel by the user.

        Parameters:

            identifier (str) : Identifier used as the root key of the JSON output.

        Returns:

            str : JSON string with outputs
        """
        self.__mineSuite__.allPredictions = self._all_predictions()

        return self.__mineSuite__.getAllPredictionsJson(identifier=identifier)

    def get_all_predictions(self, sequence_key=None):
        """
        Returns the values in dictionary form. It also allows to select the outputs of a single sequence from the
        original fasta file instead of all of them at once.

        Parameters:

            sequence_key (str, optional) : Sequence identifier specified as the FASTA header in the input
        file. It allow the user to select the output of a single sequence.

        Returns:

            reorganized_results (dict) : Dictionary which contains the output of the predictions.

        """
        result = self._all_predictions()

        if sequence_key is not None:
            results_to_reorganize = {sequence_key: result[sequence_key]}
        else:
            results_to_reorganize = result

        reorganized_results = self._organize_predictions_in_dictionary(results_to_reorganize)

        return reorganized_results

    def _organize_predictions_in_dictionary(self, results):
        new_result = {}
        for sequence in results:
            new_keys = {}

            for i, predictions in enumerate(results[sequence]):
                if predictions == 'seq' and 'seq' in results[sequence]:
                    new_keys['seq'] = results[sequence]['seq']
                    continue
                elif i == 0:
                    new_keys['seq'] = [position[0] for position in results[sequence][predictions]]
                if type(results[sequence][predictions]) == list or type(results[sequence][predictions]) == np.array or type(results[sequence][predictions]) == np.ndarray:
                    new_keys[predictions] = [position[1] for position in results[sequence][predictions]]
                else:
                    new_keys[predictions] = results[sequence][predictions]

            new_result[sequence] = new_keys

        return new_result

class MultipleSeq():
    """
    Class to handle all the MSA related inputs, it calculates the aligned
    predictions and plots accordingly.

    """

    def __init__(self):
        """
            Instates the predManager class required for all the methods below.

        """
        self._predManager = predManager()

    def from_aligned_file(self, path_to_msa, tools=[]):
        """
        This method has the responsibility of running the asked predictions when
        the input is an MSA file.

        Parameters:

            path_to_msa (str): Path to the file where the alignment is located.

            tools (list[str]) : List of tools to be ran. Any combination of the
            following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"

        Returns:

            obj: self
        """
        self.type = "from_msa"
        return self._predManager.run_predictors(path_to_msa, predTypes=tools)

    def from_two_msa(self, path_to_msa1, path_to_msa2, tools=[]):
        """
        This method has the responsibility of running the asked predictions when
        the input are two MSA files to be compared.

        Parameters:

            path_to_msa1 (str): Path to the 1st file where the alignment is
            located.

            path_to_msa2 (str): Path to the 2nd file where the alignment is
            located.

            tools (list[str]) : List of tools to be ran. Any combination of the
            following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"

        Returns:

            obj: self
        """
        self.type = "from_msa"
        msa = MsaManager()
        msa.t_coffe_MSA_aligner([path_to_msa1, path_to_msa2])
        return self._predManager.run_predictors(msa.out_file_name,
                                                msa_map=msa.msa_dict,
                                                predTypes=tools)

    def from_json(self, path_to_json, tools=[0], output_dir=""):
        """
        This method has the responsibility of running the asked predictions when
        the input is a json file defining sequence variants (predefined format).

        Parameters:

            path_to_json (str): Path to the json file with the sequence variants
            tools (list[str]) : List of tools to be ran. Any combination of the
            following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"
            output_dir (str): Path to the output fasta file created by reading the json file

        Returns:

            obj: self
        """
        self.type = "from_json"
        return self._predManager.run_predictors_json_input(path_to_json,
                                                           predTypes=tools)

    def from_blast(self, path_to_sequence, tools=[], blast_file_name = None, mut_option = None, mut_position=None, mut_residue=None):
        """
        This method has the responsibility of running the asked predictions when
        the input is a fasta file with a single sequence from which an alignment
        is generated with the BLAST hits.

        Parameters:

            path_to_sequence (str): Path to the fasta file where the sequence of
            interest is located.

            tools (list[str]) : List of tools to be ran. Any combination of the
            following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"

        Returns:

            obj: self
        """
        self.type = "from_msa"
        blast = BlastManager(path_to_sequence, file_name=blast_file_name, mut_option=mut_option, mut_position=mut_position, mut_residue=mut_residue)
        blast.run_qblast()
        return self._predManager.run_predictors(blast.aligned_file,
                                                mutation=None,
                                                predTypes=tools)

    def from_uniref(self, uniprotKB_id, tools=[]):
        """
        This method has the responsibility of running the asked predictions when
        the input is a UniprotKB identifier from which an alignment is generated
        with the UniRef hits (Top 25).

        Parameters:

            uniprotKB_id (str): UniprotKB identifier

            tools (list[str]) : List of tools to be ran. Any combination of the
            following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"

        Returns:

            obj: self
        """
        self.type = "from_msa"
        uniref = UniRef50Manager(uniprotKB_id, 'uniref')
        return self._predManager.run_predictors(uniref.aligned_file,
                                                predTypes=tools)

    def get_all_predictions_msa(self, sequence_key=None):
        """
        This method has the responsibility of returning the predictions mapped
        to the alignment. A sequence identifier can be used to retrieve only the
        desired predictions.

        Parameters:

            sequence_key (str): Sequence identifier

        Returns:

            obj: Aligned predictions
        """
        if sequence_key is not None:
            return self._predManager.allAlignedPredictions[sequence_key]
        else:
            return self._predManager.allAlignedPredictions

    def get_all_predictions_msa_distrib(self):
        """
        This method has the responsibility of returning the distribution of the
        predictions for all the positions in the alignment (Top-outlier, third-
        quartile, median, 1st quartile, bottom-outlier)

        Returns:

            obj: Distribution of the aligned predictions

        """
        return self._predManager.distrib

    def plot(self):
        """
        This method has the responsibility of returning the according prediction
        plots depending on the input.

        Returns:

            obj: Plots for the selected input

        """
        plotter = Plotter()
        if self.type == "from_msa":
            return plotter.plot_msa_distrib(self._predManager.jsondata_list)

        elif self.type == "from_json":
            return plotter.plot_json(self._predManager.allAlignedPredictions)
