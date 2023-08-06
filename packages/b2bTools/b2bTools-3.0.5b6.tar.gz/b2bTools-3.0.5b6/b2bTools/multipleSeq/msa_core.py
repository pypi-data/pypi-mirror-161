import os, os.path, sys
import requests
import time
import urllib.parse
import urllib.request
import json
import argparse
import numpy as np
import pandas as pd
from Bio import SeqIO
from Bio.Blast import NCBIWWW, NCBIXML
from b2bTools.general.Io import B2bIo
from b2bTools.multipleSeq.Predictor import MineSuiteMSA
from b2bTools.singleSeq.Predictor import MineSuite
from b2bTools.general.plotter import Plotter

###############################################################################
###############################################################################

class UniRef50Manager:
    def __init__(
            self,
            UniProtKB_idA,
            fasta_name_A = None,
            ):
        # UniProtKb IDs
        self.idA = self._retrieve_id(UniProtKB_idA)
        # UniRef50 IDs
        self.UniRef50_idA = self._retrieve_UniRef50_id(self.idA)

        # UniRef50 members and protein sequences
        self.UniRef50_membersA_fasta = \
            self._retrieve_UniRef50_members_fasta(
                    self.UniRef50_idA,
                    fileName=fasta_name_A,
                    )

    def UniProtKB_Mapping(self,
            query,
            fileName=None,
            From="ACC",
            To="ACC",
            Format="fasta",
            Columns="",
            limit="10"
    ):
        """Implementation of the UniProtKB mapping REST api.

        UniProtKB provides an REST API to map one database to another,
        similar to the webservice (https://www.uniprot.org/uploadlists/).
        More information about the working of the API can be found on:
        https://www.uniprot.org/help/api_idmapping

        Parameters
        ----------
        query : str
            The query parameter accepts a sequence of identifiers separated
            by a space or newline character.  The format of the identifiers
            depends on the database which is mapped from.
        fileName : str (Default=None)
            The destination path of the file that is downloaded.  If just a
            name is specified, the file is stored in the directory from
            which the function was executed.  Additionaly the relative or
            absolute path can be specified.
        From : str (Default='ACC')
            The database from which the identifiers are mapped. The
            available databases are listed on:
            https://www.uniprot.org/help/api_idmapping
        To : str (Default='ACC')
            The database to which the identifiers are mapped. The
            available databases are listed on:
            https://www.uniprot.org/help/api_idmapping
        Format : str (Default='fasta')
            The file format of the mapped identifiers.  The available format
            are:
            html | tab | xls | fasta | gff | txt | xml | rdf | list | rss
        Columns : str (Default="")
            The column information to be downloaded for each entry when the
            format is tab or xls.

        Returns
        -------
        response : str
            The content of the downloaded file in string format
        """

        """ The Download of the file is tried 10 times.  Each time the
        function waits a bit longer. Sometimes remote servers are busy and
        repeating a failed request helps.
        """
        for i in range(10):
            try:
                url = 'https://www.uniprot.org/uploadlists/'
                params = {
                    "query": query,
                    "from": From,
                    "to": To,
                    "format": Format,
                    "columns": Columns,
                    "limit": limit
                }
                data = urllib.parse.urlencode(params)
                data = data.encode('utf-8')
                req = urllib.request.Request(url, data)
                with urllib.request.urlopen(req) as f:
                    response = str(f.read(), encoding="utf-8")

                if fileName:
                    # Write content to file
                    with open(fileName, "w") as f:
                        # To limit the number of hits (Otherwise align is too slow)
                        response = "\n>".join(response.split("\n>")[:25])
                        f.write(response)
                return response
            except:
                print(
                    "request failed, wait for",
                    i * 5,
                    "seconds and try again",
                )
                time.sleep(i * 5)


    def _retrieve_id(
            self,
            UniProtKB_id,
            ):
        """ Retrieve the UniProtKB id.

        Sometimes, UniProtKB updates identifiers.  This method maps the
        a UniProtKB identifier to its own database to retrieve the
        latest version of this identifier.

        Parameters
        ----------
        UniProtKB_id : str
            The UniProtKB_id identifier (can be outdated).

        Returns
        -------
        new_UniProtKB_id : str
            When the UniProtKB_id is outdated, the up to date identifier
            is returned instead.  Otherwise, the original identifier
            is returned.
        """
        new_UniProtKB_id = self.UniProtKB_Mapping(
                UniProtKB_id,
                Format="list",
                ).strip()
        return new_UniProtKB_id

    def _retrieve_UniRef50_id(
            self,
            UniProtKB_id,
            ):
        """ Retrieve the UniRef50 identifier.

        UniProtKB clusters all of the protein sequences by sequence
        identity, called UniRef groups.  All members of a UniRef50 group
        will have at most 50 percent sequence identity.

        Parameters
        ----------
        UniProtKB_id : str
            The UniProtKB_id identifier (can be outdated).

        Returns
        -------
        UniRef50_id : str
            The UniRef50 identifier.
        """
        UniRef50_id = self.UniProtKB_Mapping(
                UniProtKB_id,
                From="ACC",
                To="NF50",
                Format="list",
                ).strip()
        return UniRef50_id

    def _parse_fasta(
            self,
            fasta_string,
            ):
        """ Parse fasta string into dictionary.

        This function parses the fasta file (in string format) into a
        dictionary of protein sequences.

        Parameters
        ----------
        fasta_string : str
            A fasta file in string format.

        Returns
        -------
        fasta_dictionary : dict
            The fasta file in dictionary format.
                key : ID
                value : protein sequence
        """
        fasta_dictionary = dict()
        fasta_lines = (line for line in fasta_string.split("\n"))
        for line in fasta_lines:
            if line.startswith(">"):
                Id = line.replace(">","")\
                    .split("|")[1]
                fasta_dictionary[Id] = ""
            else:
                fasta_dictionary[Id] += line.strip()
        return fasta_dictionary

    def _retrieve_UniRef50_members_fasta(self, UniRef50_id, fileName=None):
        """Retrieve fasta file of UniRef50 members.

        All members of an UniRef50 cluster have a sequence identity of
        50% or more.  This means they are homologues to each other.
        The UniProtKB mapping API is used to retrieve those members in
        fasta format.  The resulting string is subsequently parsed to a
        dictionary.

        Parameters
        ----------
        UniRef50_id : str
            The UniRef50 identifier.
        fileName : str
            Name of the fasta file.

        Returns
        -------
        UniRef50_members_fasta : dict
            Returns a dictionary of the members and their protein
            sequence.
                key : UniProtKB ID
                value : protein sequence
        """
        # if no fileName give, create generic one
        if not fileName:
            fileName = "{}.fasta".format(UniRef50_id)
        # Retrieve fasta string with UniProtKB mapping service
        UniRef50_members_fasta_str = self.UniProtKB_Mapping(
                UniRef50_id,
                From="NF50",
                To="ACC",
                Format="fasta",
                fileName=fileName
                )

        # Parse string into dictionary of protein sequences
        # UniRef50_members_fasta = self._parse_fasta(UniRef50_members_fasta_str)

        # Run the MSA using all the seqs in the fasta file found
        self.aligned_file = '{}_tcof.aln'.format(fileName.split('.')[0])
        cmd = "t_coffee {} -output=fasta_aln -outfile={}".format(
        fileName, self.aligned_file)
        os.system(cmd)

###############################################################################
###############################################################################

class BlastManager:
    def __init__(self, seq, file_name = None, mut_option = None, mut_position = None, mut_residue = None):
        self.rrm_seq = seq
        self.target_seq = []
        with open(self.rrm_seq, 'r') as f:
            for rec in SeqIO.parse(f, 'fasta'):
                self.target_seq = [res for res in rec.seq]
                break  # If the fasta file provided have more than one seq it
                # will only process the first one

        self.target_seq = ''.join(self.target_seq)

        if file_name:
            self.file_name = file_name
        else:
            self.file_name = str(
                input('Write the output filename for the BLAST results'
                    ' (String without extension nor spaces):\n'
                    '>>>') + '_blast.xml')
        if not mut_option:
            mut_option = input('Do you want to generate a mutated sequence?:\n'
                '(y = Yes; n = No) >>>')

        if mut_option == 'y':
            self.mutated_seq = self.mutator(self.target_seq, mut_position=mut_position, mut_residue=mut_residue)

        else:
            self.mutated_seq = None

    def mutator(self, prot_seq, mut_position = None, mut_residue = None):
        #     Mutagenicity test, mutate the target sequence and add it
        if mut_position:
            mut_pos = mut_position
        else:
            mut_pos = int(
                input('Select one position in the sequence to mutate:\n' +
                    prot_seq + '\n>>>'))

        print('You have selected {}{} to mutate'.format(
            prot_seq[mut_pos], mut_pos))

        if mut_residue:
            mut_res = mut_residue
        else:
            mut_res = str(input('Select the residue to mutate to:\n' +
                                'A, C, D, E, F, G, H, I, K, L, M, N, P, Q, '
                                'R, S, T, V, W, Y' +
                                '\n>>>'))

        self.mutation = prot_seq[mut_pos] + str(mut_pos) + mut_res

        self.mutated_seq = list(prot_seq)
        self.mutated_seq[mut_pos] = mut_res
        return(self.mutated_seq)

    # Function to run the online-based version of BLAST (qblast) and generate
    # the output xml file
    def run_qblast(self, blast_prog='blastp', db='refseq_protein'):
        fasta_string = open(self.rrm_seq).read()
        result_handle = NCBIWWW.qblast(blast_prog, db, fasta_string,
                                       format_type='XML')

        with open("{}".format(self.file_name), "w") as out_handle:
            out_handle.write(result_handle.read())

        self.parse_blast(self.file_name)

    # Parse the xml file with blast results generated in te function above
    def parse_blast(self, file_name):
        print('Running BLAST')
        # Debug line to input the xml file manually instead of running qblast
        result_handle = open(file_name)
        blast_record = NCBIXML.read(result_handle)

        # Define the column names that we wanna have in the final table
        column_names = ["accesion_version", "sequence_aligned",
                        "alignment_length", "identity", "coverage", "e_value"]
        df = pd.DataFrame(columns=column_names)

        # Parse the aligment file by calculating the coverage and identities
        # and filter the results according to those and the e-value as well
        self.filepath = '{}.txt'.format(
            self.file_name.split('.')[0])

        print(self.filepath)
        with open(self.filepath, 'w+') as the_file:
            # If the file is empty append first the target & mutated sequence
            if os.stat(self.filepath).st_size == 0:
                the_file.write('>target_sequence\n')
                the_file.write(self.target_seq + '\n')
                if self.mutated_seq:
                    the_file.write('>mutated_sequence\n')
                    the_file.write(''.join(self.mutated_seq) + '\n')

            # Keep blast results with ID > 0.9, cov > 0.9, e-value < 0.04
            for alignment in blast_record.alignments:
                for hsp in alignment.hsps:
                    coverage = hsp.align_length / blast_record.query_length
                    identity = hsp.identities / hsp.align_length
                    if identity > 0.9 and coverage > 0.9 and hsp.expect < 0.04:
                        acc_version = alignment.title.split("|")[1]
                        the_file.write('>{}\n'.format(acc_version))
                        the_file.write(
                            '{}'.format(hsp.sbjct.replace('-', '')) +
                            '\n')

        # Run the MSA using all the BLAST matches found
        self.aligned_file = '{}_tcof.aln'.format(self.file_name.split('.')[0])
        cmd = "t_coffee {} -output=fasta_aln -outfile={}".format(
            self.filepath, self.aligned_file)
        os.system(cmd)


###############################################################################
###############################################################################

class MsaManager:
    def __init__(self):
        print('Running MsaManager')

    # Function that uses t-coffee software to align two MSAs
    def t_coffe_MSA_aligner(self, msa_files):
        if os.path.exists('msa_tmp.aln'):
            os.remove('msa_tmp.aln')
        self.out_file_name = 'msa_tmp.aln'
        self.msa_dict = {}

        for file in msa_files:
            filename = file.split('/')[-1].split('.')[0]
            self.msa_dict[filename] = []
            f = open(file, "r")
            self.msa_dict[filename] = [l.split('>')[1].split('\n')[0] for
                                       l in f if l.startswith('>')]

        msa_files_tcof = ','.join(msa_files)
        cmd = "t_coffee -quiet -profile={} -outfile={}".format(msa_files_tcof,
                                                        self.out_file_name)
        os.system(cmd)


###############################################################################
###############################################################################

class predManager:
    def __init__(self):
        print("Biophysical predictor class running...")
        self.ms = MineSuiteMSA()

    # Function to run all the predictors over an MSA file:
    # DynaMine, EFoldMine and Disomine)
    def run_predictors(self, msa_file, predTypes = [], msa_map = None, mutation=None):
        # msa_map is a dictionary containing the original alignment with
        # file name (key) and sequence names (value), required when an
        # alignment of 2 MSAs is provided (None by default)
        self.ms.predictSeqsFromMSA(msa_file, predTypes=predTypes)

        self.mutated_seq_preds = None

        # Same but now mapped to reference sequence ID in MSA, gaps are None
        self.ms.predictAndMapSeqsFromMSA(msa_file, dataRead=True)
        self.allAlignedPredictions = self.ms.allAlignedPredictions

        self.jsondata_list = []

        try:
            # Create the results folder if it's not there yet
            if not os.path.exists("/results"):
                os.mkdir("/results")
        except BaseException:
            pass

        # When we work with an alignment of MSAs
        if msa_map != None:
            for key in msa_map.keys():
                # The two variables below are updated to include only the
                # sequences from one of the source MSA files at a time
                self.ms.allAlignedPredictions = {
                    sel_key: self.allAlignedPredictions[sel_key] for sel_key
                    in msa_map[key]}
                self.ms.allSeqIds = [
                    key for key in self.ms.allAlignedPredictions.keys()]

                # Same but now mapped to full MSA, distributions of scores.
                self.jsondata_list.append(self.ms.getDistributions())

        # When we work with a single MSA
        else:
            # Same but now mapped to full MSA, distributions of scores.
            self.jsondata_list.append(self.ms.getDistributions())

    def run_predictors_json_input(self, json_file, predTypes = [], output_dir=""):
        msa_file = B2bIo.json_to_fasta_variants(json_file, output_dir)
        print(predTypes)
        self.ms.predictSeqsFromMSA(msa_file, predTypes=predTypes)

        # Same but now mapped to full MSA, gaps are None
        self.ms.predictAndMapSeqsFromMSA(msa_file, dataRead=True)
        self.allAlignedPredictions = self.ms.allAlignedPredictions

###############################################################################
###############################################################################

if __name__ == '__main__':
    # Input files parser
    parser = argparse.ArgumentParser(description='Input handler')

    parser.add_argument('-aligned_file', type = str, nargs=1,
                        help = 'Runs the predictors over an aligned file')

    parser.add_argument('-qblast', type=str,
                        help='The input protein sequence/s in fasta format'
                            ' to run qBLAST and the biophysical predictions')

    parser.add_argument('-align', type=str, nargs=2,
                        help='MSA files to be aligned and biophysically compared')

    parser.add_argument('-uniref', type=str, nargs=1,
                        help='UniprotKB id to find related sequences and compare them biophysically')

    parser.add_argument('-json', type=str, nargs=1,
                        help='JSON file with the WT sequence and the variants defined')

    args = parser.parse_args()

    if args.aligned_file:
        print(args.aligned_file)
        PRED = predManager()
        PRED.run_predictors(args.aligned_file[0])

    # Run blastp with fasta file as input
    elif args.qblast:
        RRM = BlastManager(args.qblast)
        print("Running BLAST (This step may take a few minutes)")
        RRM.run_qblast()
        PRED = predManager()
        PRED.run_predictors(RRM.aligned_file, mutation = RRM.mutation)

    # Align two MSA files, run the predictors and plot the mapped results
    elif args.align:
        MSA = MsaManager()
        MSA.t_coffe_MSA_aligner(args.align)
        PRED = predManager()
        PRED.run_predictors(MSA.out_file_name, msa_map = MSA.msa_dict)

    # UniprotKB id to find related sequences and compare them biophysically
    elif args.uniref:
        print(args.uniref)
        uniref = UniRef50Manager(args.uniref[0], 'uniref')
        PRED = predManager()
        PRED.run_predictors(uniref.aligned_file)

    # To define several sequences and variant through a json file format
    elif args.json:
        print(args.json)
        PRED = predManager()
        PRED.run_predictors_json_input(args.json[0])

    else:
        print("Not argument provided or invalid argument")
