import numpy as np
import time

from b2bTools.singleSeq.Predictor import MineSuite
from b2bTools.general.Io import B2bIo

class MineSuiteMSA(MineSuite):

  scriptName = "b2bTools.msaBased.Predictor"

  def predictSeqsFromMSA(self, msaFile, gapCode='-', predTypes=[]):

    # This will read in alignment, should automatically detect format. Code is in general/Io.py
    self.seqAlignments = self.readAlignments(msaFile, resetAlignRefSeqID=True, gapCode=gapCode)

    seqs = []
    for seqId in self.seqAlignments.keys():
      seqs.append((seqId,self.seqAlignments[seqId].replace(gapCode,'')))

    self.predictSeqs(seqs, predTypes= predTypes)

    # Now self.allPredictions will give you the predictions for all the individual sequences in the MSA!

  def predictAndMapSeqsFromMSA(self, msaFile, gapCode='-', dataRead=False,
                               predTypes=[]):

    # Read in data only if not yet present - can re-use this function within instance of class if data already present!
    if not dataRead:
      self.predictSeqsFromMSA(msaFile,gapCode=gapCode, predTypes=predTypes)

    self.allSeqIds = list(self.seqAlignments.keys())
    self.allSeqIds.sort()

    # All the current prediction types
    self.predictionTypes = self.allPredictions[self.allSeqIds[0]].keys()

    self.allAlignedPredictions = {}
    sequenceInfo = {}

    for seqId in self.allSeqIds:

      alignment = self.seqAlignments[seqId]
      seqIndex = 0

      sequenceInfo[seqId] = []
      self.allAlignedPredictions[seqId] = {}

      for predictionType in self.predictionTypes:
        self.allAlignedPredictions[seqId][predictionType] = []

      for alignIndex in range(len(alignment)):
        if alignment[alignIndex] == self.gapCode:
          for predictionType in self.predictionTypes:
            self.allAlignedPredictions[seqId][predictionType].append(None)
        else:
          resName = self.allPredictions[seqId]['backbone'][seqIndex][0]

          assert resName == alignment[alignIndex] or resName == 'X', "Amino acid code mismatch {}-{}".format(resName,
                                                                                                             alignment[
                                                                                                               alignIndex])

          sequenceInfo[seqId].append(alignment[alignIndex])

          for predictionType in self.predictionTypes:
            try:
              valueTuple = self.allPredictions[seqId][predictionType][seqIndex]
              resName, predValue, *other_values = valueTuple
              self.allAlignedPredictions[seqId][predictionType].append(predValue)
            except ValueError:
              raise ValueError("Predicted value of type '%s' not found for input sequence '%s'" % (predictionType, seqId))

          seqIndex += 1

    self.allAlignedPredictions['sequence'] = sequenceInfo

  def filterByRefSeq(self,refSeqId):

    assert refSeqId in self.allSeqIds,  'Reference sequence ID {} missing in current prediction information!'.format(refSeqId)

    # Here filter so that get back values in reference to the sequence ID that is given.

  def getDistributions(self):

    distribKeys = ('median', 'thirdQuartile', 'firstQuartile', 'topOutlier', 'bottomOutlier')
    numDistribKeys = len(distribKeys)

    # Now generate the info for quartiles, ... based on the alignRefSeqID, first entry in alignment file
    self.alignedPredictionDistribs = {}
    for predictionType in self.predictionTypes:
      self.alignedPredictionDistribs[predictionType] = {}
      for distribKey in distribKeys:
        self.alignedPredictionDistribs[predictionType][distribKey] = []

    # Loop over whole alignment
    alignmentLength = len(self.seqAlignments[self.allSeqIds[0]])

    for alignIndex in range(alignmentLength):
      for predictionType in self.predictionTypes:
        predValues = [self.allAlignedPredictions[seqId][predictionType][alignIndex] for seqId in self.allSeqIds if
                      self.allAlignedPredictions[seqId][predictionType][alignIndex] != None]

        distribInfo = self.getDistribInfo(predValues)

        for i in range(numDistribKeys):
          self.alignedPredictionDistribs[predictionType][distribKeys[i]].append(distribInfo[i])

    self.jsonData = B2bIo.getAllPredictionsJson_msa(self, results = self.alignedPredictionDistribs)
    return self.jsonData

  def getDistribInfo(self,valueList, outlierConstant = 1.5):
    # JR: I put this try-except cause in some MSA we may have only one sequence
    # so the distribution values cannot be calculated
    try:
      median = np.median(valueList)
      upper_quartile = np.percentile(valueList, 75)
      lower_quartile = np.percentile(valueList, 25)
      IQR = (upper_quartile - lower_quartile) * outlierConstant

      return (median, upper_quartile, lower_quartile,upper_quartile + IQR,lower_quartile - IQR)

    except:
      return (None, None, None, None, None)
