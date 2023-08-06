## Single protein sequence based tools

This directory contains tools that require only a single protein amino acid sequence as input.
Multiple sequences can be provided as input, but the predictions themselves will always relate
to a single protein.

_Note: this was checked against the original EFoldMine, results are the same!_

### Input specifications

* Sequences
    * As list/tuple of (seqId,sequenceString) tuples
    * seqId is the sequence identifier, **note that this might get converted in the output**
* Function
    * Currently using predictSeqs(), suggestions welcome
 
### Output

* Each class produces a self.allPredictions dictionary of underneath form that can be accessed in-memory
    * self.allPredictions[seqId][predictionType] = [(aaTypeString,predValue), ...]
    