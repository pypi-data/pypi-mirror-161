# -*- coding: utf-8 -*-
from os import path
import pathlib
import tempfile
import sys
import subprocess

class PsiPredRuntimeError(RuntimeError):
    pass

CURRENT_PSIPRED_DIR     = path.dirname(path.abspath(__file__))
DATA_DIR                = path.join(CURRENT_PSIPRED_DIR, 'psipred', 'data')
WEIGHTS_DAT_FILEPATH    = path.join(DATA_DIR, 'weights.dat')
WEIGHTS_DAT2_FILEPATH   = path.join(DATA_DIR, 'weights.dat2')
WEIGHTS_DAT3_FILEPATH   = path.join(DATA_DIR, 'weights.dat3')
WEIGHTS_P2_DAT_FILEPATH = path.join(DATA_DIR, 'weights_p2.dat')

current_platform = sys.platform.lower()

if current_platform == 'linux':
    binary_dir = 'linux'
elif current_platform == 'darwin': # MacOS hosts
    binary_dir = 'osx'
else:
    raise NotImplementedError(f'Platform not supported yet: {current_platform}')

SEQ2MTX  = path.join(CURRENT_PSIPRED_DIR, 'psipred', 'bin', binary_dir, 'seq2mtx')
PSIPRED  = path.join(CURRENT_PSIPRED_DIR, 'psipred', 'bin', binary_dir, 'psipred')
PSIPASS2 = path.join(CURRENT_PSIPRED_DIR, 'psipred', 'bin', binary_dir, 'psipass2')

# Notes (ADIAZ): Changing file flags inside Docker containers tends to fail,
# so that, these binaries have been pushed with the right permissions in order
# to avoid changing the flags in run-time.
# for exec_path in [SEQ2MTX, PSIPRED, PSIPASS2]:
#     if path.exists(exec_path):
#         try:
#             os.chmod(exec_path, int('777', 8))
#         except PermissionError as err:
#             print(f"There was a problem while updating permissions of file: {exec_path}.", err)


def run(input, tmpfolder = None):
    """
    params:
        - input: (str) fasta_filename
        - tmpfolder: (str) path to temp directory
    """

    if not path.exists(input):
        raise PsiPredRuntimeError(f"Invalid FASTA file path. Please check: {input}")

    if not tmpfolder:
        tmpfolder = tempfile.mkdtemp()

    fasta = pathlib.Path(input)
    base_name  = fasta.stem

    mtx_filepath   = path.join(tmpfolder, f"{base_name}.mtx")
    ss_filepath    = path.join(tmpfolder, f"{base_name}.ss")
    ss2_filepath   = path.join(tmpfolder, f"{base_name}.ss2")
    horiz_filepath = path.join(tmpfolder, f"{base_name}.horiz")

    with open(mtx_filepath, "w") as mtx_file:
        seq2mtx_proc = subprocess.run([SEQ2MTX, input], stdout=mtx_file)

    if seq2mtx_proc.returncode != 0:
        raise PsiPredRuntimeError(f"There was an error executing SEQ2MTX. Return code={seq2mtx_proc.returncode}")

    with open(ss_filepath, "w") as ss_file:
        psipred_proc = subprocess.run([PSIPRED, mtx_filepath, WEIGHTS_DAT_FILEPATH, WEIGHTS_DAT2_FILEPATH, WEIGHTS_DAT3_FILEPATH], stdout=ss_file)

    if psipred_proc.returncode != 0:
        raise PsiPredRuntimeError(f"There was an error executing PSIPRED. Return code={seq2mtx_proc.returncode}")

    with open(horiz_filepath, "w") as horiz_file:
        psipass2_proc = subprocess.run([PSIPASS2, WEIGHTS_P2_DAT_FILEPATH, '1', '1.0', '1.0', ss2_filepath, ss_filepath], stdout=horiz_file)

    if psipass2_proc.returncode != 0:
        raise PsiPredRuntimeError(f"There was an error executing PSIPASS2. Return code={seq2mtx_proc.returncode}")
