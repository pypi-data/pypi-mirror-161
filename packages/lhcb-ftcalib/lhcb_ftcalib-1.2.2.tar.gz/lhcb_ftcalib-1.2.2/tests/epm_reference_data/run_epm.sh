#!/bin/bash
EPM=$1
set -e

function calibrate {
    cd $1
    $EPM calibrate.py |& tee calibrate.log
    mv EspressoCalibratedPerformanceSummary.csv EspressoCalibratedPerformanceSummary.csv.orig
    mv EspressoPerformanceSummary.csv EspressoPerformanceSummary.csv.orig
    $EPM write.py |& tee write.log
    cd ..
}

calibrate Bd_bspline4_logit
calibrate Bd_bspline5_mistag
calibrate Bd_nspline3_mistag
calibrate Bd_nspline4_logit
calibrate Bd_poly1_logit
calibrate Bd_poly1_mistag
calibrate Bd_poly2_mistag
calibrate Bs_poly1_mistag
calibrate Bu_poly1_mistag
calibrate Bd_poly1_mistag_sweights

cd combination_test
$EPM combine.py |& tee combine.log
cd ..
