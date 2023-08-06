#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import tempfile
from .runpsipred_single import run

class DisomineRuntimeError(RuntimeError):
    pass

GAP_SYMBOL = '-'

class psipred:

    def __init__(self, tmpfold, single_sequence=True):
        if not single_sequence:
            raise NotImplementedError("Only Single Sequence prediction has been implemented so far.")

        self.tmpfold = tmpfold


    def predict(self, seq, seq_ID, base_name):
        predictions = []

        fasta_filename = os.path.join(self.tmpfold, f'{base_name}.fasta')
        ss2_filename   = os.path.join(self.tmpfold, f'{base_name}.ss2')
        horiz_filename = os.path.join(self.tmpfold, f'{base_name}.horiz')
        ss_filename    = os.path.join(self.tmpfold, f'{base_name}.ss')
        mtx_filename   = os.path.join(self.tmpfold, f'{base_name}.mtx')

        try:
            with open(fasta_filename, 'w') as fasta_file:
                fasta_file.write('>{0}\n{1}'.format(seq_ID, seq))

            # Executes PSIPRED binary
            run(fasta_filename, self.tmpfold)

            # Reads the PSIPRED output file .ss2
            with open(ss2_filename, 'r') as ss2_file:
                ss2 = ss2_file.readlines()

            for ss2_row in ss2[2:]:
                ss2_row_fields = ss2_row.strip().split()

                if len(ss2_row_fields) > 0:
                    predictions += [[float(ss2_row_fields[3]), float(ss2_row_fields[4]), float(ss2_row_fields[5])]]
        except Exception as exc:
            raise DisomineRuntimeError("There was an unexpected error while running Disomine's binaries") from exc
        finally:
            # Deletes the temp files
            if os.path.exists(fasta_filename):
                os.remove(fasta_filename)

            if os.path.exists(ss2_filename):
                os.remove(ss2_filename)

            if os.path.exists(horiz_filename):
                os.remove(horiz_filename)

            if os.path.exists(ss_filename):
                os.remove(ss_filename)

            if os.path.exists(mtx_filename):
                os.remove(mtx_filename)

        return predictions


def build_vector(seq, dmPredictions, base_name=None, seqID=None, TYPE=None, sw=None, nomeseq=None, tmpfold=None):
    vector = []
    sequence_length = len(seq)
    seq_nogap = seq.replace(GAP_SYMBOL, '')

    for i in range(sequence_length):
        vector += [[]]

    # nfeatures = 0

    for curr_fea in TYPE.split(','):
        if curr_fea.startswith('dyna') or curr_fea == 'ef':

            if curr_fea == 'dyna_coil':
                v_dyna = [dmPredictions['coil']]
            elif curr_fea == 'dyna_sheet':
                v_dyna = [dmPredictions['sheet']]
            elif curr_fea == 'dyna_helix':
                v_dyna = [dmPredictions['helix']]
            elif curr_fea == 'dyna_side':
                v_dyna = [dmPredictions['sidechain']]
            elif curr_fea == 'dyna_back':
                v_dyna = [dmPredictions['backbone']]
            elif curr_fea == 'ef':
                v_dyna = [dmPredictions['earlyFolding']]

            effect = 0  ## We could remove it and only use vector_index. Validate hypothesis.

            for vector_index in range(len(vector)):
                if seq[vector_index] != GAP_SYMBOL:
                    # print i
                    for s in range(-sw, sw + 1):
                        if effect + s < 0:
                            vector[vector_index] += [0]
                        elif effect + s >= len(seq_nogap):
                            vector[vector_index] += [0]
                        else:
                            vector[vector_index] += [v_dyna[0][effect + s][1]]

                    effect += 1

        elif curr_fea == 'psipred':
            if not tmpfold:
                tmpfold = tempfile.mkdtemp()

            psidpred_runner = psipred(tmpfold)
            v_psipred = psidpred_runner.predict(seq_nogap, seqID, base_name=base_name)

            effect = 0

            for vector_index in range(len(vector)):
                if seq[vector_index] != GAP_SYMBOL:
                    for s in range(-sw, sw + 1):
                        if effect + s < 0:
                            vector[vector_index] += [0] * 3
                        elif effect + s >= len(seq_nogap):
                            vector[vector_index] += [0] * 3
                        else:
                            vector[vector_index] += v_psipred[effect + s]

                    effect += 1

        else:
            assert False, f'{curr_fea} IS NOT A FEATURE'

    # Notes (ADIAZ): nfeatures is always 0, thus this loop can be omitted
    # for sequence_index in range(sequence_length):
    #     if seq[sequence_index] == GAP_SYMBOL or seq[sequence_index] == '.':
    #         vector[sequence_index] += [GAP_SYMBOL] * nfeatures

    return vector
