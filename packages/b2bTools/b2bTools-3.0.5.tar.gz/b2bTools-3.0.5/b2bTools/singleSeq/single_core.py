# File to handle different inputs and run the predictors (single seq level)
import os, os.path, sys
import json
import argparse
import numpy as np
import pandas as pd
from Bio.PDB import *
import urllib.request
from b2bTools.general.Io import B2bIo
from b2bTools.singleSeq.Predictor import MineSuite
from b2bTools.general.plotter import plot_results

# Input files parser
parser = argparse.ArgumentParser(description='Input handler')

parser.add_argument('-pdb', action='store', nargs = '*',
                    help='Use pdb id or file as input to get the sequence and \
                          run the predictors')

parser.add_argument('-uniprot', type=str,
                    help='Uniprot ID code')

parser.add_argument('-fasta', type=str,
                    help='The input protein sequence/s in fasta format')

parser.add_argument('-nef', type=str,
                    help='The input protein file in nef format')

args = parser.parse_args()

aa_coder = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
     'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
     'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
     'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}

###############################################################################
###############################################################################

def run_predictors(seqs, id):
    tools = B2bIo()
    ms = MineSuite()
    ms.predictSeqs(seqs)

    with open("tmp_file.json", 'w') as fp:
        json_data = ms.getAllPredictionsJson(id)
        json.dump(json_data, fp)
        input_csv = input("Do you want to save the predictions in a text file? (Y/N)")

        if input_csv == "Y":
            tools.json_preds_to_csv_singleseq(json_data)
            filename = json_data["id"].split("/")[-1].split(".")[0]
            print("Results succesfully saved in results/{}.txt".format(filename))

    plot_results("tmp_file.json", msa_like=1,
                 mutation="")


###############################################################################
###############################################################################

if __name__ == '__main__':
    if args.pdb:
        # Iput ID: The two argument values must be the pdb Id and the chain Id
        if len(args.pdb) == 2:
            pdb_id_input = args.pdb[0]
            chain_id_input = args.pdb[1]
            print ("PDB code and chain:", pdb_id_input, chain_id_input)
            full_pdb_id = [pdb_id_input.upper(), chain_id_input]
            seqs = []
            if len(full_pdb_id) > 1 and len(full_pdb_id[0]) == 4:
                try:
                    url = 'https://www.rcsb.org/fasta/chain/'
                    pdburl = url + ".".join(full_pdb_id) + '/download'
                    response = urllib.request.urlopen(pdburl)
                    data = response.read()
                    PDB_seq = data.decode('utf-8')
                    seqs.append((full_pdb_id[0], PDB_seq.split("\n")[1]))
                    run_predictors(seqs, full_pdb_id[0])

                except:
                    print("Entry not found / some error occured")

            else:
                print("Invalid entry check your input")

        # Input pdb file: The argument value must be the path to the pdb file
        if len(args.pdb) == 1:
            print("TODO")
            # Add warning for pdb
            # get sequence from pdb file

    elif args.uniprot:
        uniprotID = args.uniprot
        run_predictors(B2bIo.retrieve_seq_uniprot(uniprotID), uniprotID)

    elif args.fasta:
        tools = B2bIo()
        seqs = tools.readFasta(args.fasta)
        run_predictors(seqs, args.fasta)

    elif args.nef:
        tools = B2bIo()
        info = tools.readNefFileSequenceShifts(args.nef)
        sequence = [(args.nef ,''.join([aa_coder[resname[0]["residue_name"]] for
                                        resname in info["A"]]))]
        run_predictors(sequence, args.nef)
