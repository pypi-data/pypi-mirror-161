.. _CLI:

Command Line Interface
======================

For common calibration procedures, lhcb_ftcalib can be called via the command line via the 
executable `ftcalib`. It is by design not feature complete in order to support the most common
calibration procedures and be simpler to maintain.::

    $ ftcalib --help 

    usage: ftcalib [-h] [-t TAGGERS [TAGGERS ...]] [-SS SSTAGGERS [SSTAGGERS ...]] [-OS OSTAGGERS [OSTAGGERS ...]] [-id ID_BRANCH] [-mode {Bu,Bd,Bs}]
               [-tau TAU] [-tauerr TAUERR] [-timeunit {ns,ps,fs}] [-weights WEIGHTS] -op {calibrate,combine,apply} [{calibrate,combine,apply} ...]
               [-write WRITE] [-selection SELECTION] [-input_cal INPUT_CAL] [-plot] [-n NMAX] [-skip SKIPFIRST]
               [-keep_branches KEEP_BRANCHES [KEEP_BRANCHES ...]] [-fun FUN FUN] [-link {mistag,logit,rlogit,probit,rprobit,cauchit,rcauchit}] [-i]
               [-filetype {root,csv}]
               rootfile

    LHCb Flavour Tagging calibration software

    positional arguments:
      rootfile              ROOT file and tree to read tagging data from. (example: "file.root:DecayTree")

    options:
      -h, --help            show this help message and exit
      -t TAGGERS [TAGGERS ...]
                            Enumeration of taggers to find in file. This argument will try to match partial names, e.g.
                            "MuonLatest"->"B_OSMuonLatest_TAGDEC/ETA"
      -SS SSTAGGERS [SSTAGGERS ...]
                            Enumeration of same side taggers to find in file. This argument will try to match partial names, e.g.
                            "MuonLatest"->"B_OSMuonLatest_TAGDEC/ETA"
      -OS OSTAGGERS [OSTAGGERS ...]
                            Enumeration of opposite side taggers to find in file. This argument will try to match partial names, e.g.
                            "MuonLatest"->"B_OSMuonLatest_TAGDEC/ETA"
      -id ID_BRANCH         Name of the B meson id branch
      -mode {Bu,Bd,Bs}      Calibration mode
      -tau TAU              Name of the decay time branch
      -tauerr TAUERR        Name of the decay time uncertainty branch
      -timeunit {ns,ps,fs}  Decay time unit
      -weights WEIGHTS      Name of the per-event weight branch
      -op {calibrate,combine,apply} [{calibrate,combine,apply} ...]
                            What to do with the loaded taggers
      -write WRITE          Name of a file where to store calibrated branches and calibrations. Example: (-write myFile:atree) writes to myFile to TTree
                            "atree"
      -selection SELECTION  Selection expression (example: 'eventNumber%2==0;eventNumber%2==1'), selection after semicolon is used for combination calibration
                            (optional)
      -input_cal INPUT_CAL  JSON file of the input calibrations
      -plot                 If set, plots calibration curves
      -n NMAX               Number of events to read from file. Default:All
      -skip SKIPFIRST       Number of events to skip from the start. Default: 0
      -keep_branches KEEP_BRANCHES [KEEP_BRANCHES ...]
                            List of branches or branch wildcards or text files containing branches
      -fun FUN FUN          CalibrationFunction followed by number of parameters per flavour (default: ['poly', '2']). Available calibration functions:
                            ['poly', 'nspline', 'bspline']
      -link {mistag,logit,rlogit,probit,rprobit,cauchit,rcauchit}
                            Link function (default: mistag)
      -i                    Interactive mode, will ask for confirmation
      -filetype {root,csv}  Filetype to use instead of root files


Argument description
....................

Tagger lists ``-t [...] -SS [...] -OS [...]``
*********************************************
These arguments mark the start of lists of taggers that should be grouped together.
Example:::

    ftcalib file:tree -OS OSMuonL OSElectionL Charm -SS SSPion SSProt [...]

Tagger names do not need to be fully written out. If that leads to ambiguitites
("OSMu" -> "OSMuonLatest_TAGETA"/"OSMuon_TAGETA") or no match is found, an
exception is raised. Taggers after ``-t`` will be combined using the generic
name ``Combination``, ``-SS`` and ``-OS`` Combinations will be called
``SS_Combination`` and ``OS_Combination``, respectively

ID branch ``-id``
*****************
The ID branch is given via the argument ``-id``. The branch in the tuple should
contain a list of MC particle ids of either Bd, Bu or Bs mesons. If the branch
contains the values -1 and 1 instead, a warning is raised and [1, -1] is
treated as [B0, Bbar] etc. If more than one ID is found, an exception is
raised.

Calibration mode ``-mode``
**************************
The calibration mode can be either "Bu", "Bd" or "Bs". If Bd or Bs is used, a
decay time branch must be provided using ``-tau <branch>``.

Decay time branches ``-tau -tauerr -timeunit``
**********************************************
The decay time branch is specified with the ``-tau`` argument. Optionally, the
decay time uncertainty branch can be provided via the ``-tauerr`` argument, in
which case the time-dependent mixing probability will be analytically convolved
with gaussians of these widths. In the Bs case, where :math:`\Delta\Gamma\neq
0` this has to be done numerically. By default, the assumed decay time unit is
nanoseconds, but this can be modified using the ``-timeunit`` argument with
"ns", "ps" or "fs".

Per event weights ``-weights``
******************************
The per-event weight branch is specified using ``-weights``.

Use Error Propagation ``-propagate_errors``
*********************
Error propagation is enabled by the ``-propagate_errors`` argument.
This option will have two effects:
    * Mistag error branches will be written to the tuples
    * The combination algorithm will propagate these errors to the combined Tagger

Calibration operations
**********************
The list of calibration operations to be performed is passed via the ``-op`` argument
Example:::

    ftcalib file:tree [...] -op calibrate combine calibrate

This will calibrate the single tagger collections, combine them into
combinations and calibrate the combinations. Whether a combination should be
performed and calibrated is optional.

Applying calibrations
*********************
The list of operations to be performed for applying calibrations is passed via the ``-op`` argument
Example:::

    ftcalib file:tree [...] -op apply combine -input_cal cal.json

This will read the calibration file cal.json, build the calibration functions
stored in it, and apply it to the taggers in the tuple that have the same names
as the ones in cal.json. If that is not the case, the API should be used where
a name mapping can be specified. Afterwards the calibrated taggers are combined
and the combination calibration is applied immediately afterwards.

Output file name ``-write``
***************************
It is recommended to always specify the name of the output file via ``-write``.
This name will be used for the calibration json file and by setting this
option, a root file containing the calibrated branches will be written.
Optionally, the name of a TTree can be specified with ``-write
myOutputFile:MyDecayTree`` which will create ``myOutputFile.root`` with TTree
``MyDecayTree`` and ``myOutputFile.json`` for calibration results.

Event selections ``-selection``
*******************************
With the ``-selection`` argument, a selection string can be specified
(example: ``(eventNumber%2==0)and(B_PT>1000)``). This string is interpreted by
``pandas.DataFrame.query`` and must be compatible to its specifications. To use
a different selection for combination calibrations, the second-stage-selection
can be specified after a semicolon (example: ``eventNumber%2==0;eventNumber%2==1``)

**Warning**: unsigned 64bit integers are converted into signed 64bit integers,
because of ``pandas.DataFrame.query`` limitations. This will raise a warning

Calibration plots ``-plot``
***************************
If the ``-plot`` argument is used, plots of the calibrated taggers will be
written to the directory from where ``ftcalib`` is called. At the moment, only
calibration plots overlaying the calibration curve vs data are supported.

Additional branches ``-keep_branches``
**************************************
With the ``-keep_branches`` argument, additional branches from the input root file
can be selected which are copied to the output root file.
Example::

   ftcalib -keep_branches B_PX *PT branches.txt <...>

This command would transfer the branch ``B_PX``, all branches ending with ``PT``
and all branches (or branch wildcards) contained in the text file ``branches.txt``.
In ``branches.txt`` each entry must be on a single line. To check the validity of 
the selected branches it is recommended to use the ``-i`` option.

Specifying the GLM calibration
******************************
By default, first degree polynomials and the mistag link are used for all
calibrations. Using the ``-fun`` argument, a different calibration function
class following by its degree can be specified. Example: ``-fun poly 2`` will
choose calibration parabolas. With the ``-link`` argument, an alternative link
function can be chosen (see ``ftcalib --help``). These settings are then used
for **all** calibrations. If this is not intended, consider using the API
instead where the choice of calibration for each tagger can be fine-tuned.

Examples
========
Calibrating a set of taggers
.......................................
To calibrate the vertex charge tagger "OSVtxCh_TAGDEC/ETA" and the OS Charm
tagger "OSCharm_TAGDEC/ETA" we list the two taggers as tagger name hints via
``-t``, specify an id Branch and we choose B+ as the calibration mode. Then we
specify what operations should be performed via the option ``-op``. In this
case we just want to "calibrate" the taggers. Lastly, we specify an output file
pattern for the calibrations and calibrated mistag branches via `-write`.::

    ftcalib file.root:DecayTree -t Vtx Charm -id B_ID -mode Bu -op calibrate -write vtxAndCharm

Calibrating and combining taggers
.................................
In this example, we group the SS and OS tagger together:::

    ftcalib file.root:DecayTree -OS Vtx Charm -SS SSPion SSProton -id B_ID -mode Bu -op calibrate combine calibrate -write calib_result

Calibrating taggers in a file and applying the calibrations
...........................................................
Applying calibration is done in a separate step. First, we determine
calibrations on a control channel and then we use the calibration file as the
input calibration for some target data.::

    ftcalib file.root:DecayTree -OS Vtx Charm -SS SSPion SSProton -id B_ID -mode Bu -op calibrate combine calibrate -write calib_result
    ftcalib targetdata.root:DecayTree -OS Vtx Charm -SS SSPion SSProton -op apply combine -write applied_calibration -input_cal calib_result.json
