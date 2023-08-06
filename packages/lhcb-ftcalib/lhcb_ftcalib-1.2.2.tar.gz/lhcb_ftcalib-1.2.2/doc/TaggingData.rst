TaggingData module
==================

Every :class:`Tagger` object owns an object of type :class:`TaggingData` to keep track
of the tagging statistics and tagging performances. This data can be accessed under the 
`stats` member of a :class:`Tagger` object and does not need to be instantiated by hand.
In fact, it should not be instantiated by hand, as a Tagger objects updates
the internal data of its :class:`TaggingData` members.

Example use
-----------
The Tagging Data module is usually a member of a Tagger object and is not initialized on its own.
Its intended use is as follows. 

.. code-block:: python

   import uproot
   import lhcb_ftcalib as ft

   df = uproot.open("data.root")["DecayTree"].arrays(library="pd")

   tagger = ft.Tagger("OSmu", df.eta, df.dec, df.B_ID, "Bd", tau_ps=df.B_TAU, weight=df.sweight)

   tagger.set_calibration(ft.PolynomialCalibration(2, ft.link.mistag))

   tagger.calibrate()

   OSmu_stats = tagger.stats  # type(OSmu_stats) == TaggingData

   print(OSmu_stats.Nt, "Tagged events in tuple")
   print("Tagging power", OSmu_stats.tagging_power(calibrated=False))
   print("Calibrated tagging power", OSmu_stats.tagging_power(calibrated=True))

If this class is absolutely needed independetly of a tagger, the user must initialize
its decay time data and update the calibrated statistics manually by calling its private (undocumented) methods.

Conventions
-----------

* A tagged event is an event with nonzero tagging decision

  **Edge cases**
    * :math:`\omega>0.5`: Counts as untagged and is truncated to :math:`\omega\equiv 0.5, d\equiv 0`.
    * :math:`\omega<0`: Counts as tagged but mistag is truncated to :math:`\omega\equiv 0`
      as otherwise link functions may crash and such values are not well motivated.
    * :math:`\omega\in(0, 0.5)\wedge d=0`: counts as untagged by the main definition.
    * :math:`\omega=0.5\wedge d\neq 0`: Events counts as tagged.
* A selected event is every event which the user has selected via the `selection` argument when constructing the tagger

.. autoclass:: lhcb_ftcalib.TaggingData
   :members:
   :undoc-members:
   :show-inheritance:
