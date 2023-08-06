datafile  = "../reference.root"
TupleName = "BD_POLY1_MISTAG_SWEIGHTS"
Nmax      = -1
DoCalibrations = 1

CalibrationMode   = "Bd"
CalibrationLink   = "MISTAG"
CalibrationDegree = 1
CalibrationModel  = "POLY"
UseNewtonRaphson  = 0

BranchID = "FLAV_DECAY"
ProductionAsymmetry = 0

TauUnits  = "ps"
UseTau    = 1
BranchTau = "TAU"
UseTauErr = 0

UseWeight = 1
WeightFormula = "WEIGHT"

OS_Muon_Use            = 1
OS_Muon_Write          = 0
OS_Muon_BranchDec      = "TOY0_DEC"
OS_Muon_BranchProb     = "TOY0_ETA"
SaveCalibrationsToXML = 1
