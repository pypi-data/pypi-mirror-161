TaggerCollection module
=======================

The TaggerCollection class defines common procedures that are applied to
a collections of taggers, like calibrations and combinations and plotting
of results calibration curves.

Example use
-----------
The TaggerCollection module is the recommended way of calibrating a set of taggers in the same dataset.

.. code-block:: python

   import uproot
   import lhcb_ftcalib as ft

   df = uproot.open("data.root")["DecayTree"].arrays(library="pd")

   taggers = ft.TaggerCollection()
   taggers.create_tagger("OSmu", df.OSmu_eta, df.OSmu_dec, df.B_ID, "Bd", tau_ps=df.B_TAU, weight=df.sweight)  # Same aruments as Tagger class
   taggers.create_tagger("OSK", df.OSK_eta, df.OSK_dec, df.B_ID, "Bd", tau_ps=df.B_TAU, weight=df.sweight)
   taggers.create_tagger("OSe", df.OSe_eta, df.OSe_dec, df.B_ID, "Bd", tau_ps=df.B_TAU, weight=df.sweight)

   taggers.set_calibration(ft.PolynomialCalibration(3, ft.link.mistag))

   # We may need a different function for a specific tagger. This is not possible via the command line.
   taggers["OSe"].set_calibration(ft.NSplineCalibration(3, ft.link.logit)) 

   # The following function prints a lot of statistics and tables and calibrates all taggers in the collection.
   taggers.calibrate(quiet=False)

   # Now we could combine the taggers into one. If we would use "calibrated=False" here we 
   # would combine the raw single tagger statistics, which is not usually what we want.
   tagger_combination = taggers.combine_taggers("MyCombination", calibrated=True)

   # And calibrate this tagger again
   tagger_combination.calibrate()


.. autoclass:: lhcb_ftcalib.TaggerCollection
   :members:
   :undoc-members:
   :show-inheritance:
