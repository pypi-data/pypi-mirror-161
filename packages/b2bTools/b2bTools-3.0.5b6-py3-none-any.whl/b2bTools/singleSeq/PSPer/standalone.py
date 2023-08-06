# -*- coding: utf-8 -*-
import sysconfig, os
from b2bTools.singleSeq.PSPer.phase_transition_hmm import phase_hmm
import string
import numpy as np


def leggifasta(database):
		f=open(database)
		uniprot=f.readlines()
		f.close()
		dizio={}
		for i in uniprot:
			if i[0]=='>':
					uniprotid=i.strip('>\n')
					dizio[uniprotid]=''
			else:
				dizio[uniprotid]=dizio[uniprotid]+i.strip('\n').upper()
		return dizio

def standalone(input_obj):
	features='dyna_back,psipred,ef,dyna_side'
	window=4
	verbose=0

	def check_sequences(seqs):
		for i in list(seqs.keys()):
			if i=='extra_predictions':
				continue
			if not seqs[i].isalpha():
				return {'error':'invalid char in sequence '+i}
			if len(seqs[i])>3000:
				#print len(seqs[i])
				return {'error':'sequence '+i+' too long, maximum length is 3000 amino acids'}
			if len(seqs[i])<20:
				#print len(seqs[i])
				return {'error':'sequence '+i+' short, minimum length is 20 amino acids'}

		return True

	def load_model():
		mod = phase_hmm()
		mod.fit()

		scaler = None

		return mod, scaler

	def format_output(disorder, viterbi, seqs, features):
		protein_id_keys = list(disorder.keys())

		out=[]
		for protein_id_index in range(len(protein_id_keys)):
			protein_id = protein_id_keys[protein_id_index]
			current_features = features[protein_id]

			for feature_index in range(5):
				actual = current_features[:, feature_index]
				base   = current_features[:, 0]

				assert len(actual) == len(base)

			entry={}

			features[protein_id] = np.array(current_features)
			entry['proteinID'] = protein_id
			entry['sequence'] = seqs[protein_id]
			entry['protein_score']=disorder[protein_id]
			entry['viterbi']=viterbi[protein_id] if protein_id in viterbi else np.full(len(seqs[protein_id]), '')
			entry['complexity']=list(features[protein_id][:,0])
			entry['arg']=list(features[protein_id][:,1])
			entry['tyr']=list(features[protein_id][:,2])
			entry['RRM']=list(features[protein_id][:,3])
			entry['disorder']=list(features[protein_id][:,4])

			out+=[entry]

		return { 'results': out }

	def predict_fasta(sequence_input, model, crunch=100):
		if type(sequence_input)==str:
			try:
				fasta_sequences=leggifasta(sequence_input)
			except:
				return {'error':"problems in the fasta file"}
		elif type(sequence_input)==dict:
			fasta_sequences=sequence_input
		else:
			return {'error':'internal error, wrong object passed to the standalone, it must be either a dict or a string'}

		check = check_sequences(fasta_sequences)
		if not check:
			return check

		# targets=list(fasta_sequences.keys())[:]
		# results_dict={}
		# cont=0
		# dyna={}
		# side={}
		# ef={}

		built_vector = model.build_vector(fasta_sequences)
		results_dict = model.predict_proba(built_vector)
		viterbi = model.viterbi(built_vector)

		dict_features = {}
		printable_characters = string.printable
		for id in built_vector.keys():
			seq_vector = []

			for seq_vector_element in built_vector[id]:
				temp_seq_vector = []
				# feature_counter = 0

				for element_feature in seq_vector_element:
					feature_char_index = printable_characters.index(element_feature)
					temp_seq_vector += [float(feature_char_index)]

					# if feature_counter == 1 or feature_counter == 2:
					# 	feature_char_index = printable_characters.index(element_feature)
					# 	temp_seq_vector += [float(feature_char_index)]
					# else:
					# 	feature_char_index = printable_characters.index(element_feature)
					# 	temp_seq_vector += [float(feature_char_index)]

					# 	feature_counter += 1

				seq_vector += [temp_seq_vector]

			dict_features[id] = np.array(seq_vector)

		results = format_output(results_dict, viterbi, fasta_sequences, dict_features)
		return results

	# This should not be necessary with new disomine setup, commented out
	#clean_psipred_tmp()
	phase_hmm_instance, _ = load_model()
	results = predict_fasta(input_obj, phase_hmm_instance)

	return results

def main(args):
	#print standalone("example.fasta")
	fasta_sequences=leggifasta('input_files_examples/example_toy.fasta')
	fasta_sequences['extra_predictions']=False
	print(standalone(fasta_sequences))
	#from memory_profiler import memory_usage
	#mem_usage = memory_usage(standalone,interval=0.01)
	#print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
	#print('Maximum memory usage: %s' % max(mem_usage))
	#cProfile.run('standalone("example.fasta")')

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
