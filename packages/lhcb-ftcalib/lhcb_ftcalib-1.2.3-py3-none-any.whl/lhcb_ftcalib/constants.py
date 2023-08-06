# Oscillation parameters
DeltaM_d     = 0.5065
DeltaGamma_d = 0
DeltaM_s     = 17.741
DeltaGamma_s = 0.082

# Covariance scaling for weighted fits
CovarianceCorrectionMethod = "SquaredHesse"  # "SumW2", "None"

# Propgate uncertainties of the calibrated mistags through tagger combination
propagate_errors = False

# Calculate uncertainties of the calibrated mistags. May cost some time, so this is optional
calculate_omegaerr = True

# Use averaged representation of the calibration to write calibrated mistag to
# tuples. This is probably not optimal, but this mimics the EPM behaviour
ignore_mistag_asymmetry_for_apply = True
