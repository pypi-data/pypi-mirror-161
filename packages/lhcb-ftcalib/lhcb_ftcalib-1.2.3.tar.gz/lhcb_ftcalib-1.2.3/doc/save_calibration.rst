Saving calibrations
===================

In order to be able to apply a flavour tagging calibration to some other data,
it needs to be saved to a file and loaded by a :class:`TargetTagger` instance
afterwards. If multiple calibrations are written to the same file they are appended.

.. autofunction:: lhcb_ftcalib.save_calibration

Calibration file format
-----------------------
The calibration file format is json and the entries are mostly self-explanatory. The less self-explanatory ones are explained below.

* Section **calibration** contains calibration function info

  * ``avg_eta``: Average mistag
  * ``flavour_style.params``: Calibration parameters and covariance in flavour specific convention
  * ``delta_style.params``: Calibration parameters and covariance in Delta parameter convention
  * ``stats``: Various event counts. Naming is matching TaggingData conventions

* Section ``uncalibrated`` contains FT performances before calibration

  * ``selected`` Performances of events in selection
  * ``overall`` Performances of full dataset
