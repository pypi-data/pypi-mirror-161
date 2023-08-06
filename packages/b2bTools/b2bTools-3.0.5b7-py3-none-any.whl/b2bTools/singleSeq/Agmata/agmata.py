#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  shiftcrypt.py
#
#  Copyright 2018  <@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import argparse
import sys
# import warnings
# warnings.filterwarnings("ignore")

from b2bTools.general.Io import B2bIo
from b2bTools.singleSeq.EFoldMine.Predictor import EFoldMine
from b2bTools.singleSeq.Agmata.sources.agmata_source import agmata

def getAgmataPredictions(seqs, efm = None):
	"""getAgmataPredictions(seqs: tuple, efm: dict)

	Uses the Agmata model to predict beta aggregation from the input sequences

	params:
	- seqs: A tuple of (SEQ ID, RESIDUES)
	- efm: EFoldMine results in a dictionary format
	"""

	# Best cutoff for aggregating, or not
	THRESHOLD = 0.015563146

	model = agmata(verbose=-1)
	model.load()

	if not efm:
		print('Running EFoldMine')
		efm = EFoldMine()
		efm.predictSeqs(seqs)

	results = model.predict(seqList = seqs, dmPredictions = efm.allPredictions)

	# Loop over sequence, set category
	for (proteinId, sequence) in seqs:
		# Initialize the results as an empty array
		efm.allPredictions[proteinId]['agmata'] = []

		# Fetch agmata results for the current protein and count the length of values
		current_sequence_agmata_results = results[proteinId]
		current_sequence_residues_count = len(current_sequence_agmata_results)

		# For each residue in the results array
		for residue_index in range(current_sequence_residues_count):
			# Residue at this residue_index
			residue = sequence[residue_index]

			# Default class: 0
			aggregation_class = 0

			# Get the current result value
			current_residue_agmata_result = current_sequence_agmata_results[residue_index]

			try:
				if type(current_residue_agmata_result) is float:
					current_aggregation_value = current_residue_agmata_result
				# elif type(current_residue_agmata_result) is tuple:
				# 	print("Reading current_aggregation_value from TUPLE", current_residue_agmata_result)
				# 	_a, current_aggregation_value, _c = current_residue_agmata_result
				else:
					raise NotImplementedError(f"Aggregating type ({type(current_residue_agmata_result)}) is not supported yet")

				# If aggregation value is greater than the THRESHOLD the class will be 1
				if current_aggregation_value > THRESHOLD:
					aggregation_class = 1

				# Replace original result with: tuple(RESIDUE (char), AGGREGATION VALUE (float), AGGREGATION CLASS (0 or 1))
				results[proteinId][residue_index] = (residue, current_aggregation_value, aggregation_class)

				# Append this result tuple to all the predicted values:
				efm.allPredictions[proteinId]['agmata'].append(results[proteinId][residue_index])
			except BaseException as e:
				print(f"Agmata has failed: residue_index={residue_index}; current_residue_agmata_result={current_residue_agmata_result}; current_aggregation_value={current_aggregation_value}; aggregation_class={aggregation_class}; THRESHOLD={THRESHOLD}")
				raise e

	return results

def run_agmata(args):
	args=args[1:]
	pa = argparse.ArgumentParser()

	pa.add_argument('-i', '--infile',
						help='the input FASTA file',
						)
	pa.add_argument('-o', '--outfile',
						help='output file',
						default=None)

	parseArgs = pa.parse_args(args)

	b2bio = B2bIo()

	try:
		seqs = b2bio.readFasta(parseArgs.infile)
	except:
		print('Error in FASTA file parsing. Please double check the format and input file name. If everything is correct, please report the bug to wim.vranken@vub.be')
		return

	results = getAgmataPredictions(seqs)

	textOutput = ""

	textOutput+= '#AA AgmataScore BinaryPrediction\n'
	for proteinId in results.keys():
		textOutput+= '# {}\n'.format(proteinId)
		for (aaCode,prediction,predClass) in results[proteinId]:
			textOutput+="{} {:7.2e} {}\n".format(aaCode,prediction,predClass)

	if parseArgs.outfile!=None:
		f = open(parseArgs.outfile, 'w')
		f.write(textOutput)
		f.close()

	else:
		print(textOutput)

	print('\nDONE')

def main(args):
	return 0

if __name__ == '__main__':
	sys.exit(run_agmata(sys.argv))
