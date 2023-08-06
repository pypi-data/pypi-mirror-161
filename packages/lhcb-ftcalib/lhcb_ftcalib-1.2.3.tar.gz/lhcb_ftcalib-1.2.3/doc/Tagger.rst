Tagger module
=============

In ftcalib, a :class:`TaggerBase` object is a collection of Tagging data sufficient to
perform or apply a flavour tagging calibration. A tagger stores its own
calibration function in the member `func`. Two Tagger classes :class:`Tagger` and
:class:`TargetTagger` are derived from :class:`TaggerBase` (which should never be
instantiated as it is supposed to be purely virtual). :class:`Tagger` is used to run a
flavour tagging calibration while :class:`TargetTagger` is supposed to load a
calibration from file and apply it to some target data, hence the name.

Example use
-----------

.. code-block:: python

   import uproot
   import lhcb_ftcalib as ft

   df = uproot.open("data.root")["DecayTree"].arrays(library="pd")

   tagger = ft.Tagger("OSmu", df.eta, df.dec, df.B_ID, "Bd", tau_ps=df.B_TAU, weight=df.sweight, selection="eta<0.49")

   tagger.set_calibration(ft.PolynomialCalibration(3, ft.link.logit))

   tagger.calibrate()

.. autoclass:: lhcb_ftcalib.Tagger.TaggerBase
   :members:
   :show-inheritance:

.. autoclass:: lhcb_ftcalib.Tagger
   :members:
   :undoc-members:
   :show-inheritance:
