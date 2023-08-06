OS_Muon_CalibrationArchive     = "OS_Muon_Calibration.xml"
datafile  = "../reference.root"
TupleName = "BD_POLY1_MISTAG_SWEIGHTS"
DoCalibrations = 0

CalibrationMode   = "Bd"
CalibrationLink   = "MISTAG"
CalibrationDegree = 1
CalibrationModel  = "POLY"
UseNewtonRaphson  = 0

TauUnits  = "ps"
UseTau    = 1
BranchTau = "TAU"

UseWeight = 1
WeightFormula = "WEIGHT"

BranchID = "FLAV_DECAY"

OS_Muon_Use            = 1
OS_Muon_Write          = 1
OS_Muon_BranchDec      = "TOY0_DEC"
OS_Muon_BranchProb     = "TOY0_ETA"
WriteCalibratedMistagBranches = 1
CalibratedOutputFile = "output.root"
