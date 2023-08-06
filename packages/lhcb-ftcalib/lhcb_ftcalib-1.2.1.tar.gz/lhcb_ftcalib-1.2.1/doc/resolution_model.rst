Decay time resolution models
============================

For the calibration of neutral B meson modes, the production flavour
is estimated with the help of the time dependent mixing probability :math:`\gamma(t)`

:math:`\gamma(t)=\displaystyle\frac{1}{2}(1-|A_\mathrm{mix}|)`

whereby :math:`A_\mathrm{mix}(t)` is the mixing asymmetry.

:math:`A_\mathrm{mix}(t)=\displaystyle\frac{\cos(\Delta m_q t)}{\cosh\left(\frac{1}{2}\Delta\Gamma_q t\right)}`.

If the decaytime measurements have uncertainties, the mixing asymmetry of an event
is effectively convoluted with a time resolution model of the given decay time uncertainty.
In the case of a single-gaussian time resolution distribution a analytical solution exists:

:math:`A_\mathrm{mix}(t) \mapsto \exp\left(-\frac{1}{2}\Delta m_q^2\sigma_t^2\right)A_\text{mix}(t)`.

For this default case the resolution model of type GaussianResolution does not
need to be passed to the Tagger constructor.  If :math:`\Delta\Gamma` is not
zero, numerical convolutions of a resolution model with widths
:math:`\sigma_{t,i}` with the mixing asymmetry is performed.

.. autoclass:: lhcb_ftcalib.resolution_model.ResolutionModel
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: lhcb_ftcalib.GaussianResolution
   :members:
   :undoc-members:
   :show-inheritance:
