#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  agmata.py
#
#  Copyright 2018 Gabriele Orlando <orlando.gabriele89@gmail.com>
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
from datetime import timedelta
import os
import sys
import gc
import pathlib, shutil, tempfile
import subprocess
import pickle
import time

import numpy as np

from b2bTools.singleSeq.DisoMine.vector_builder.vettore_gen import build_vector


class AgmataRuntimeError(RuntimeError):
	pass


class agmata():

	def __init__(self, features = 'dyna_back,dyna_coil,dyna_sheet,dyna_helix,dyna_side', sw = 1, verbose = 2):
		self.features  = features
		self.sw        = sw
		self.LEARNING  = 'log_reg'
		self.verbose   = verbose
		self.params    = [self.LEARNING, self.features, self.sw]
		self.scriptDir = str(pathlib.Path(__file__).parent.absolute())
		self.binDir    = os.path.dirname(self.scriptDir)


	def load(self, force = False):
		model_parameters_filepath                = os.path.join(self.scriptDir, '..', 'marshalled', 'model_parameters.m')
		agmata_discriminative_converted_filepath = os.path.join(self.scriptDir, '..', 'marshalled', 'agmata_discriminative_converted.m')

		with open(model_parameters_filepath, 'rb') as model_parameters_file:
			unpickler_model_parameters = pickle._Unpickler(model_parameters_file)
			unpickler_model_parameters.encoding = 'latin1'
			parameters_from_pickle = unpickler_model_parameters.load()

		# Check whether the parameters have changed or not
		if self.params != parameters_from_pickle:
			# Whether force keeping old parameters:
			if force:
				print(f'PARAMETERS CHANGED! but force == True, keeping old params({parameters_from_pickle})')

				with open(agmata_discriminative_converted_filepath, 'rb') as agmata_discriminative_converted_file:
					unpickler_agmata_discriminative_converted = pickle._Unpickler(agmata_discriminative_converted_file)
					unpickler_agmata_discriminative_converted.encoding = 'latin1'
					parameters_from_discriminative_converted_pickle = unpickler_agmata_discriminative_converted.load()

				Dp, Da, Dn = parameters_from_discriminative_converted_pickle

				self.Dp       = Dp
				self.Da       = Da
				self.Dn       = Dn
				self.params   = parameters_from_pickle
				self.LEARNING = parameters_from_pickle[0]
				self.features = parameters_from_pickle[1]
				self.sw       = parameters_from_pickle[2]

			# Or fit again
			else:
				print('PARAMETERS CHANGED! and force == False, NEW FITTING')
				self.fit() # NOTES from Adrián: Where was fit() defined? Unreachable code!
		else:
    		# When the parameters have not changed
			with open(agmata_discriminative_converted_filepath, 'rb') as agmata_discriminative_converted_file:
				unpickler_agmata_discriminative_converted = pickle._Unpickler(agmata_discriminative_converted_file)
				unpickler_agmata_discriminative_converted.encoding = 'latin1'

				parameters_from_discriminative_converted_pickle = unpickler_agmata_discriminative_converted.load()

			Dp, Da, Dn = parameters_from_discriminative_converted_pickle
			self.Dp = Dp
			self.Da = Da
			self.Dn = Dn


	def predict(self, seqList, dmPredictions):
		results = {}

		# Agmata-related variables
		agmata_suffix = self.__build_agmata_suffix__()
		agmata_exe = f"{self.binDir}/bin/agmata_c_final_{agmata_suffix}"

		# IO variables
		tmpDir                       = tempfile.mkdtemp()
		coefficient_filepath         = os.path.join(tmpDir, 'coef.tmp')
		sequence_filepath            = os.path.join(tmpDir, 'seq.tmp')
		aggregating_profile_filepath = os.path.join(tmpDir, 'aggr_profile.dat')
		best_pairings_list_filepath  = os.path.join(tmpDir, 'best_pairings_list.dat')
		pairing_mat_filepath         = os.path.join(tmpDir, 'pairing_mat.dat')

		try:
			for (proteinId, sequence) in seqList:
				results[proteinId] = self.__predict_sequence__(
					proteinId,
					sequence,
					dmPredictions[proteinId],
					coefficient_filepath,
					sequence_filepath,
					aggregating_profile_filepath,
					agmata_exe,
					tmpDir)

				# Remove temporary files
				os.remove(sequence_filepath)
				os.remove(coefficient_filepath)
				os.remove(aggregating_profile_filepath)

				# These files are not read by this code, however we are removing them just in case:
				os.remove(best_pairings_list_filepath)
				os.remove(pairing_mat_filepath)

		finally:
			shutil.rmtree(tmpDir, ignore_errors=True)

		return results


	def __predict_sequence__(self, proteinId, sequence, dmPrediction, coefficient_filepath, sequence_filepath, aggregating_profile_filepath, agmata_exe, tmpDir):
		start_time = time.process_time()

		if self.verbose >= 2:
			print('\tStarting target:', proteinId)

		# Write the sequence in fasta format inside the temp directory
		with open(sequence_filepath, 'w') as sequence_file:
			sequence_file.write(sequence + '\n')

		# Compare residues depending on the learning method
		compared_residues, len_agmata_vector = self.__compare_residues__(sequence, dmPrediction)

		# Collect coefficient lines and write the coef.tmp file
		coefficient_file_lines = self.__collect_coefficient_lines__(compared_residues, len_agmata_vector)
		with open(coefficient_filepath, 'w') as coefficient_file:
			coefficient_file.writelines(coefficient_file_lines)

		# Execute AgMata executable using the tmpDir as base directory because both seq.tmp and coef.tmp must be present
		self.__run_agmata_executable__(agmata_exe, tmpDir)

		# Read the aggregation profile generated by AgMata executable from aggr_profile.dat file
		with open(aggregating_profile_filepath, 'r') as aggregating_profile_file:
			aggregating_profile_lines = aggregating_profile_file.readlines()

		aggregating_profile = [float(aggregating_profile_value) for aggregating_profile_value in aggregating_profile_lines]

		# Log the elapsed time
		elapsed_time = time.process_time() - start_time
		if self.verbose >= 2:
			print(f'Agmata has predicted sequence: proteinId={proteinId}; total time={timedelta(seconds=elapsed_time)}')

		return aggregating_profile


	def __run_agmata_executable__(self, agmata_exe, tmpDir):
		start_time = time.process_time()

		agmataProc = subprocess.run([agmata_exe, "seq.tmp", "600", "0"], cwd=tmpDir)

		time_diff = time.process_time() - start_time
		if self.verbose >= 2:
			print(f"Agmata executable finished: return code={agmataProc.returncode}; tmpDir={tmpDir}; time={timedelta(seconds=time_diff)}")

		if agmataProc.returncode != 0:
			raise AgmataRuntimeError("Execution of agmata executable file failed (exit status {0:d}). Vars: agmata_exe={1}; tmpDir={2};".format(
				agmataProc.returncode,
				agmata_exe,
				tmpDir))


	def __compare_residues__(self, sequence, dmPrediction):
		start_time = time.process_time()

		compared_residues = []
		comparison_function = self.__find_comparison_method__()

		# Build the Agmata vector
		agmata_results = build_vector(sequence, dmPrediction, TYPE=self.features, sw=self.sw)
		agmata_vector = np.array(agmata_results)
		len_agmata_vector = len(agmata_vector)

		# Compare residues and store the results inside compared_residues
		for agmata_built_vector_index_i in range(len_agmata_vector):
			for agmata_built_vector_index_j in range(agmata_built_vector_index_i, len_agmata_vector):
				value_1 = agmata_vector[agmata_built_vector_index_i]
				value_2 = agmata_vector[agmata_built_vector_index_j]

				compared_value = comparison_function(value_1, value_2)

				compared_residues += [compared_value]

		if self.verbose >= 1:
			coefficient_number = 2 * len(compared_residues)

			print('\tnumero coefficienti:', coefficient_number)
			print('\tcoefficient number:',  coefficient_number)

		time_diff = time.process_time() - start_time
		if self.verbose >= 2:
			print(f"All the residues have been compared: residues={len_agmata_vector}; compared_residues={len(compared_residues)}; time={timedelta(seconds=time_diff)};")

		return compared_residues, len_agmata_vector


	def __collect_coefficient_lines__(self, compared_residues, residues_count):
		start_time = time.process_time()

		coefficient_file_lines = None

		if self.LEARNING == 'kde':
			coefficient_file_lines = self.__collect_coefficients_by_score_samples(compared_residues, residues_count)
		elif self.LEARNING == 'log_reg' or self.LEARNING == 'SVM':
			coefficient_file_lines = self.__collect_coefficients_by_predict_log_proba(compared_residues, residues_count)
		else:
			raise AgmataRuntimeError(f'Unknown discriminative method: {self.LEARNING}')

		time_diff = time.process_time() - start_time
		if self.verbose >= 2:
			print(f"All the coefficient lines have been collected: residues={residues_count}; lines={len(coefficient_file_lines)}; time={timedelta(seconds=time_diff)};")

		return coefficient_file_lines


	def __collect_coefficients_by_score_samples(self, compared_residues, residues_count):
		coefficient_file_lines = []
		cont = 0

		ant = self.Da.score_samples(compared_residues)
		par = self.Dp.score_samples(compared_residues)
		non = self.Dn.score_samples(compared_residues)

		for agmata_built_vector_index_i in range(residues_count):
			for agmata_built_vector_index_j in range(agmata_built_vector_index_i + 1, residues_count):
				pa = (non[cont] - par[cont]) # from: pa = -(par[cont] - non[cont])
				an = (non[cont] - ant[cont]) # from: an = -(ant[cont] - non[cont])

				file_line_content = self.__coefficient_line__(vector_1=agmata_built_vector_index_i + 1, vector_2=agmata_built_vector_index_j + 1, pa=pa, an=an)

				coefficient_file_lines.append(file_line_content)
				cont += 1

		return coefficient_file_lines


	def __collect_coefficients_by_predict_log_proba(self, compared_residues, residues_count):
		coefficient_file_lines = []
		cont = 0

		ant = self.Da.predict_log_proba(compared_residues)
		par = self.Dp.predict_log_proba(compared_residues)

		for agmata_built_vector_index_i in range(residues_count):
			for agmata_built_vector_index_j in range(agmata_built_vector_index_i, residues_count):
				pa = (par[cont][0] - par[cont][1]) # from: pa = -(par[cont][1] - par[cont][0])
				an = (ant[cont][0] - ant[cont][1]) # from: an = -(ant[cont][1] - ant[cont][0])

				file_line_content = self.__coefficient_line__(vector_1=agmata_built_vector_index_i + 1, vector_2=agmata_built_vector_index_j + 1, pa=pa, an=an)
				coefficient_file_lines.append(file_line_content)
				cont += 1

		return coefficient_file_lines


	def __find_comparison_method__(self, method = 'vicini'):
		if method == 'vicini':
			return self.__comparison_method_vicini__
		elif method == 'diff':
			return self.__comparison_method_diff__
		else:
			raise NotImplementedError("Comparison method not implemented yet.")


	def __comparison_method_diff__(self, vector_1, vector_2):
		vf = []

		if '-' in vector_1:
			for i in vector_2:
				if type(i) != str:
					vf += [i]

			return vf
		elif '-' in vector_2:
			for i in vector_1:
				if type(i) != str:
					vf+=[i]

			return vf
		else:
			for i in range(len(vector_1)):
				if type(vector_1[i])!=str:
					vf+=[abs(vector_1[i]-vector_2[i])]
				else:
					if (vector_1[i].upper(),vector_2[i].upper()) in blosum:
						vf+=[blosum[(vector_1[i].upper(),vector_2[i].upper())]]
					else:
						vf+=[blosum[(vector_2[i].upper(),vector_1[i].upper())]]

		return vf


	def __comparison_method_vicini__(self, vector_1, vector_2):
		if '-' in set(vector_1): # from: np.isin('-', vector_1)
			tmp_vector_2 = [elem for elem in vector_2 if type(elem) != str]
			return tmp_vector_2
		elif '-' in set(vector_2):
			tmp_vector_1 = [elem for elem in vector_1 if type(elem) != str]
			return tmp_vector_1
		else:
			result_vector = []

			for vector_1_index in range(len(vector_1)):
				vector_1_element = vector_1[vector_1_index]
				vector_2_element = vector_2[vector_1_index]

				if type(vector_1_element) != str:
					result_vector += [vector_1_element, vector_2_element]
				else:
    				# Note from Adrian: Where was `blosum` defined?
					if (vector_1_element.upper(), vector_2_element.upper()) in blosum:
						result_vector+=[blosum[(vector_1_element.upper(), vector_2_element.upper())]]
					else:
						result_vector+=[blosum[(vector_2_element.upper(), vector_1_element.upper())]]

			return result_vector


	def __build_agmata_suffix__(self):
		current_platform = sys.platform

		if current_platform.startswith("linux"):
			return "linux"
		elif current_platform == 'darwin':
			return 'mac'
		else:
			raise AgmataRuntimeError(f"Executable not available for this OS ({current_platform}) - please contact wim.vranken@vub.be to add it.")


	def __coefficient_line__(self, vector_1, vector_2, pa, an):
		return f"{vector_1} {vector_2} {pa} {an} 0.00000 0.00000\n" # from: str(vector_1)+' '+str(vector_2)+' '+str(pa)+' '+str(an)+' 0.00000 0.00000 \n'
