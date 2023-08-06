#!/bin/bash

function resetFolder {

    for FILETYPE in '*.tex' '*.png' '*.pdf' '*.csv' '*.xml' 'EspressoCalibrations.py' '*.root' 'output.root' 'EspressoHistograms.root' 'combined.root' '*.log'; do
        find $1 -name $FILETYPE -type f -exec rm -v {} \;;
    done

}

resetFolder Bd_bspline4_logit
resetFolder Bd_bspline5_mistag
resetFolder Bd_nspline3_mistag
resetFolder Bd_nspline4_logit
resetFolder Bd_poly1_logit
resetFolder Bd_poly1_mistag
resetFolder Bd_poly2_mistag
resetFolder Bs_poly1_mistag
resetFolder Bu_poly1_mistag
resetFolder Bd_poly1_mistag_weights
resetFolder combination_test
