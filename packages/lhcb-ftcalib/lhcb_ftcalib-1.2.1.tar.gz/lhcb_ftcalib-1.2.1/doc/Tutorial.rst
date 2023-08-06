Getting Started
===============
lhcb-ftcalib is a package that faciliates the calibration of mistag probabilities
given some raw tagging probabilities and tagging decisions and a calibration dataset.
A mistag probability (or mistag for short)
is the probability that a tagging decision is wrong. In calibration datasets containing neutral
B or Bs mesons, oscillation is taken into account.

Installation
------------

``lhcb-ftcalib`` is available in the python package index (PyPI) and also provides a command
line tool called ``ftcalib``. The command line tool is by design not feature complete,
the API should be used for non-`standard` calibrations.
``lhcb-ftcalib`` can be installed via

.. code-block::

    pip install lhcb-ftcalib

**If**, for some reason, the package could not installed from the PyPI, a manual installation is possible:

.. code-block::

   git clone https://gitlab.cern.ch/lhcb-ft/lhcb_ftcalib.git
   cd lhcb-ftcalib
   pip install -e .

The package requirements are listed in ``requirements.txt``. If, for some reason, a manual installation
of the requirements should fail, a full environment can be installed through ``pipenv``:

.. code-block::

   git clone https://gitlab.cern.ch/lhcb-ft/lhcb_ftcalib.git
   cd lhcb-ftcalib
   pipenv install -e .

Which should install fixed versions from the ``Pipefile.lock`` file.


Quickstart Example: Calibrating a Tagger
----------------------------------------

Calibrating a tagger is as easy as typing

.. code-block::

   ftcalib data.root:DecayTree -t OSElec OSMuon -op calibrate -mode Bu -id Bu_ID

This will read the file ``data.root``, search for the TTree ``"DecayTree"``,
search for a branch called ``<something>OSElec<something>ETA`` or ``DEC``, (and the same 
with "OSMuon") and
a branch called ``Bu_ID`` (usually) for the decay flavour of the B mesons,
compute tagging performance numbers, run the calibration and output the
calibration result and calibrated performance numbers to the screen. If the
arguments are somehow wrong or missing, ftcalib should tell you what the problem is.
A full list of command line arguments can be found in section *"Command Line Interface"*.
A more in-depth tutorial can be found in section "Examples".

Output
......

.. code-block::

    ----------------------------------------------------------
    --------------- lhcb_ftcalib version 1.1.6 ---------------
    ----------------------------------------------------------
     INFO  Reading data from Bu2JpsiK_2016.root:DecayTree
     INFO  The following taggers have been found
            -> "B_OSElectronLatest": eta = B_OSElectronLatest_TAGETA and d = B_OSElectronLatest_TAGDEC 
            -> "B_OSMuonLatest": eta = B_OSMuonLatest_TAGETA and d = B_OSMuonLatest_TAGDEC 
     INFO  Correlations of selected events
    ////////////////////////////////////////////////////////////////////////////////
    Tagger Fire Correlations [%]
    ////////////////////////////////////////////////////////////////////////////////
                        B_OSElectronLatest  B_OSMuonLatest
    B_OSElectronLatest          100.000000        0.548037
    B_OSMuonLatest                0.548037      100.000000 
    //////////////////////////////////////////////////////////////////////////////// 

     INFO  Correlations of selected events
    ////////////////////////////////////////////////////////////////////////////////
    Tagger Decision Correlations [%]
    ////////////////////////////////////////////////////////////////////////////////
                        B_OSElectronLatest  B_OSMuonLatest
    B_OSElectronLatest          100.000000       -0.572401
    B_OSMuonLatest               -0.572401      100.000000 
    //////////////////////////////////////////////////////////////////////////////// 

     INFO  Correlations of selected events
    ////////////////////////////////////////////////////////////////////////////////
    Tagger Decision Correlations (dilution weighted) [%]
    ////////////////////////////////////////////////////////////////////////////////
                        B_OSElectronLatest  B_OSMuonLatest
    B_OSElectronLatest          100.000000       -0.826388
    B_OSMuonLatest               -0.826388      100.000000 
    //////////////////////////////////////////////////////////////////////////////// 

     INFO  Correlations of selected events
    ////////////////////////////////////////////////////////////////////////////////
    Tagger Decision Correlations (If both fire) [%]
    ////////////////////////////////////////////////////////////////////////////////
                        B_OSElectronLatest  B_OSMuonLatest
    B_OSElectronLatest          100.000000      -12.689275
    B_OSMuonLatest              -12.689275      100.000000 
    //////////////////////////////////////////////////////////////////////////////// 

    ╔══════════════════════════════════════════════════════════════════════════╗
    ║ RAW TAGGER STATISTICS                                                    ║
    ╠════════════════════╤═════════╤═════════╤═════════════╤═════════╤═════════╣
    │ Tagger             │ #Evts   │ Σw      │ (Σw)² / Σw² │ #Tagged │ Σ_tag w │
    ├────────────────────┼─────────┼─────────┼─────────────┼─────────┼─────────┤
    │ B_OSElectronLatest │ 3083459 │ 3083459 │ 3083459.0   │ 95592   │ 95592   │
    │ B_OSMuonLatest     │ 3083459 │ 3083459 │ 3083459.0   │ 158242  │ 158242  │
    └────────────────────┴─────────┴─────────┴─────────────┴─────────┴─────────┘

    ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║ RAW TAGGING PERFORMANCES                                                                                   ║
    ╠════════════════════╤═════════════════════╤═════════════════════╤═════════════════════╤═════════════════════╣
    │ Tagger             │ Tagging Efficiency  │ Avg. Mistag Rate    │ Effective Mistag    │ Tagging Power       │
    ├────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
    │ B_OSElectronLatest │ ( 3.1002 ± 0.0099)% │ (44.7286 ± 0.1608)% │ (37.0274 ± 0.0204)% │ ( 0.2087 ± 0.0009)% │
    │ B_OSMuonLatest     │ (  5.132 ± 0.0126)% │ (42.1835 ± 0.1241)% │ (35.6071 ± 0.0161)% │ ( 0.4252 ± 0.0014)% │
    └────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘

    Basis representation for B_OSElectronLatest
    P_0(x) = 1 
    P_1(x) = x -0.3899 
    Basis representation for B_OSMuonLatest
    P_0(x) = 1 
    P_1(x) = x -0.3706 
    /////////////////////////
    //// Running calibrations 
    -------------------- B_OSElectronLatest calibration --------------------
     INFO  iminuit version 2.12.1
     INFO  Starting minimization for B_OSElectronLatest
     INFO  Selection keeps 3083459(3083459 weighted) out of 3083459(3083459) events (100.0%)
    I MnSeedGenerator Initial state: FCN =        65927.6881 Edm =        720.999519 NCalls =     17
    I VariableMetricBuilder Start iterating until Edm is < 0.0001 with call limit = 680
    I VariableMetricBuilder    0 - FCN =        65927.6881 Edm =        720.999519 NCalls =     17
    I VariableMetricBuilder    1 - FCN =        65201.7584 Edm =       1.913408457 NCalls =     26
    I VariableMetricBuilder    2 - FCN =       65199.56759 Edm =     0.00281798927 NCalls =     36
    I VariableMetricBuilder    3 - FCN =       65199.56432 Edm =   4.530618872e-07 NCalls =     46
     INFO  Minimum found
     INFO  Covariance matrix accurate

    -------------------- B_OSMuonLatest calibration --------------------
     INFO  iminuit version 2.12.1
     INFO  Starting minimization for B_OSMuonLatest
     INFO  Selection keeps 3083459(3083459 weighted) out of 3083459(3083459) events (100.0%)
    I MnSeedGenerator Initial state: FCN =        107635.094 Edm =       899.3197947 NCalls =     17
    I VariableMetricBuilder Start iterating until Edm is < 0.0001 with call limit = 680
    I VariableMetricBuilder    0 - FCN =        107635.094 Edm =       899.3197947 NCalls =     17
    I VariableMetricBuilder    1 - FCN =       106723.0122 Edm =       4.117860154 NCalls =     26
    I VariableMetricBuilder    2 - FCN =          106718.1 Edm =     0.01999129401 NCalls =     36
    I VariableMetricBuilder    3 - FCN =       106718.0769 Edm =   9.448887067e-07 NCalls =     46
     INFO  Minimum found
     INFO  Covariance matrix accurate

    ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║ FINAL CALIBRATION PARAMETERS                                                                   ║
    ╠════════════════════╤══════════════════╤══════════════════╤══════════════════╤══════════════════╣
    │ Tagger             │ p0               │ p1               │ Δp0              │ Δp1              │
    ├────────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
    │ B_OSElectronLatest │  0.0572 ± 0.0016 │ -0.2358 ± 0.0234 │  -0.004 ± 0.0032 │  0.0718 ± 0.0468 │
    │ B_OSMuonLatest     │   0.051 ± 0.0012 │ -0.1057 ± 0.0194 │  0.0026 ± 0.0025 │ -0.0215 ± 0.0388 │
    └────────────────────┴──────────────────┴──────────────────┴──────────────────┴──────────────────┘

    ╔══════════════════════════════════════════════════════════════════════════╗
    ║ CALIBRATED TAGGER STATISTICS                                             ║
    ╠════════════════════╤═════════╤═════════╤═════════════╤═════════╤═════════╣
    │ Tagger             │ #Evts   │ Σw      │ (Σw)² / Σw² │ #Tagged │ Σ_tag w │
    ├────────────────────┼─────────┼─────────┼─────────────┼─────────┼─────────┤
    │ B_OSElectronLatest │ 3083459 │ 3083459 │ 3083459.0   │ 75619   │ 75619   │
    │ B_OSMuonLatest     │ 3083459 │ 3083459 │ 3083459.0   │ 148382  │ 148382  │
    └────────────────────┴─────────┴─────────┴─────────────┴─────────┴─────────┘

    ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║ CALIBRATED TAGGING PERFORMANCES                                                                                                                    ║
    ╠════════════════════╤═════════════════════╤═════════════════════╤═════════════════════════════════════════╤═════════════════════════════════════════╣
    │ Tagger             │ Tagging Efficiency  │ Avg. Mistag Rate    │ Effective Mistag                        │ Tagging Power                           │
    ├────────────────────┼─────────────────────┼─────────────────────┼─────────────────────────────────────────┼─────────────────────────────────────────┤
    │ B_OSElectronLatest │ ( 2.4524 ± 0.0088)% │ (43.4587 ± 0.1803)% │ (41.6251 ± 0.0126(stat) ± 0.1788(cal))% │ ( 0.0688 ± 0.0003(stat) ± 0.0029(cal))% │
    │ B_OSMuonLatest     │ ( 4.8122 ± 0.0122)% │ (41.6951 ±  0.128)% │ (40.0307 ± 0.0137(stat) ± 0.1248(cal))% │ ( 0.1913 ± 0.0007(stat) ± 0.0048(cal))% │
    └────────────────────┴─────────────────────┴─────────────────────┴─────────────────────────────────────────┴─────────────────────────────────────────┘


     ■■■ Warning summary ■■■
    B_OSElectronLatest Tagger
    [OverflowWarning] 19973 calibrated mistag values > 0.5
    B_OSMuonLatest Tagger
    [OverflowWarning] 9860 calibrated mistag values > 0.5


Interpretation of output
........................
The output should be mostly self-explanatory. The following info is printed:

    * A list of identified tagger branches
    * Various kinds of tagger correlations (see :obj:`TaggerCollection.correlation <lhcb_ftcalib.TaggerCollection.correlation>` for the mathematical definitions)
    * A **"RAW TAGGER STATISTICS"** table containing

      * Contains the number of events in the branches (:obj:`TaggingData.N <lhcb_ftcalib.TaggingData.N>`)
      * The sum of event weights (:obj:`TaggingData.Nws <lhcb_ftcalib.TaggingData.Nws>`)
      * The effective number of events (:obj:`TaggingData.Neffs <lhcb_ftcalib.TaggingData.Neffs>`)
      * The number of tagged events (:obj:`TaggingData.Nts <lhcb_ftcalib.TaggingData.Nts>`)
      * The sum of event weights of tagged events (:obj:`TaggingData.Nwts <lhcb_ftcalib.TaggingData.Nwts>`)
     
    * A **"RAW TAGGING PERFORMANCES"** table containing flavour tagging performance numbers before the calibration

      * Tagging Efficiency (:obj:`TaggingData.tagging_efficiency <lhcb_ftcalib.TaggingData.tagging_efficiency>`)
      * Average Mistag Rate (:obj:`TaggingData.mistag_rate <lhcb_ftcalib.TaggingData.mistag_rate>`)
      * Effective Mistag (:obj:`TaggingData.effective_mistag <lhcb_ftcalib.TaggingData.effective_mistag>`)
      * Tagging Power (:obj:`TaggingData.tagging_power <lhcb_ftcalib.TaggingData.tagging_power>`)

    * A basis representation of the calibration function (In this case it is the default: First degree polynomial, identity (mistag) link
    * iminuit minimization output
    * A **"FINAL CALIBRATION PARAMETERS"** containing the calibration parameters of the chosen model
    * A **"CALIBRATED TAGGER STATISTICS"** table containing the updated event statistics. The numbers in this table can differ from the raw numbers if :math:`\omega>0.5`
    * A **"CALIBRATED PERFORMANCES TABLE"** contains the performance numbers od the calibrated tagging data
    * Finally, warnings are printed in case of mistag over -or underflow.

