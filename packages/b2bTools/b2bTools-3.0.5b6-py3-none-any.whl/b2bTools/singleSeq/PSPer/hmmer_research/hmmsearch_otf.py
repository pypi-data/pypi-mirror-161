#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hmmsearch_otf.py
#
#  Copyright 2018 scimmia <scimmia@scimmia-ThinkPad-L540>
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  parseHmmer.py
#
#  Copyright 2018 Daniele Raimondi <daniele.raimondi@vub.be>
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

import os
import tempfile
from b2bTools.singleSeq.PSPer.Constants import hmmbuild_bin, hmmscan_bin

def parseBoundaries(line):
	# qwwe  42 IFVGQLDKETTREELNRRFSTHGKIQDINLIFK---PTNIFAFIKYETEEAAAAALESENHAIFLNKTMH 108
	tmp = line.strip().split()
	return tmp[1], tmp[-1]

def parsePosteriori(line):
	tmp = line.strip().split()
	r = []
	for i in tmp[0]:
		p = castPosterior(i)
		if p == -1:
			continue
		r.append(p)
	return r

def castPosterior(v):
	if v == "*":
		return 10
	elif v == ".":
		return -1
	return int(v)

def parseOut(f):
	with open(f) as ifp:
		lines = ifp.readlines()

	alscores = []
	domains = []
	length = -1
	l = 0

	while l < len(lines):

		if "Scores for complete sequences" in lines[l]:
			if "[No hits" in lines[l+5]:
				return None, None
			else:
				tmp = lines[l+4].strip().split()
				#print tmp
				bitscore = float(tmp[1])
				evalue = float(tmp[3])
				alscores.append(( bitscore, evalue))
		if "Domain annotation for each sequence" in lines[l]:
			while l < len(lines):
				if "== domain" in lines[l]:
					start, end = parseBoundaries(lines[l+3])
					domains.append((int(start), int(end), parsePosteriori(lines[l+4])))
					l+=4
				l+=1
				if "Internal pipeline statistics summary:" in lines[l]:
					break
		if "residues searched)" in lines[l]:
			tmp = lines[l].strip().split()
			#print tmp
			length = int(tmp[3][1:])

		l += 1

	return domains, length

def getFeatsFromHmmer(domains, length):

	if not domains:
		return None

	hmmer_features = [0] * length

	for domain in domains:
		start = domain[0]
		end = domain[1]
		j = start - 1

		while j < end:
			a = domain[2].pop(0)
			hmmer_features[j] = a
			j += 1

	return hmmer_features

def main():
	a, l =  parseOut("output")

	#print a, l
	#raw_input()
	b = getFeatsFromHmmer(a,l)
	#print b
	c=hmmer_wrapper()
	c.fit_hmmer()
	print (c.predict({'a':'AAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','B':'VYVGNLGNNGNKTELERAFGYYGPLRSVWVARNPPGFAFVEFEDPRDAADAVRELDGRTLCGCRVR'}))

class hmmer_wrapper:
	def __init__(self, root = ''):
		self.root = root
		self.ali_file = root + 'rrm_align.pfam'
		self.phase_trans_file = root + 'phase_trans.hmm'
		self.hmmbuild_bin = hmmbuild_bin
		self.hmmscan_bin = hmmscan_bin


	def fit_hmmer_command(self):
		return f'{self.hmmbuild_bin} {self.phase_trans_file} {self.ali_file} > /dev/null'


	def hmmscan_command(self, temp_hmmer_output_file, temp_fasta_file):
		return f'{self.hmmscan_bin} -o {temp_hmmer_output_file} {self.phase_trans_file} {temp_fasta_file}'


	def fit_hmmer(self):
		os.system(self.fit_hmmer_command())


	def predict(self, seqs):
		hmmer_results = {}

		for seq_key in seqs.keys():
			current_sequence = str(seqs[seq_key])

			temp_fasta_file = tempfile.NamedTemporaryFile(delete=False, prefix='tmp_', suffix='.fasta')
			temp_hmmer_output_file = tempfile.NamedTemporaryFile(delete=False, prefix='out_hmmer_', suffix='tmp')

			try:
				with open(temp_fasta_file.name, 'w') as f:
					f.write(f'>tmp\n{current_sequence}\n')

				os.system(self.hmmscan_command(temp_hmmer_output_file.name, temp_fasta_file.name))

				domains, length = parseOut(temp_hmmer_output_file.name)
				predicted_features_from_hmmer = getFeatsFromHmmer(domains, length)

				if not predicted_features_from_hmmer:
					predicted_features_from_hmmer = [0] * len(current_sequence)

				hmmer_results[seq_key] = predicted_features_from_hmmer
			finally:
				os.remove(temp_fasta_file.name)
				os.remove(temp_hmmer_output_file.name)

		return hmmer_results


if __name__ == '__main__':
	a=hmmer_wrapper()
	print (a.predict({'a':'AAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','B':'VYVGNLGNNGNKTELERAFGYYGPLRSVWVARNPPGFAFVEFEDPRDAADAVRELDGRTLCGCRVR'}))
