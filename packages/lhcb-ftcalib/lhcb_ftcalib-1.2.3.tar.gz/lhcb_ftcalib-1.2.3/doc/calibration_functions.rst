Calibration functions
=============================

The raw mistag predictions are calibrated to better model the actual 
mistag probability :math:`\eta\mapsto\omega(\eta)`. The available
calibration functions are listed here.

GLM Polynomials
---------------

.. autoclass:: lhcb_ftcalib.PolynomialCalibration
   :members:
   :undoc-members:
   :show-inheritance:

Cubic Spline GLM
----------------

.. autoclass:: lhcb_ftcalib.NSplineCalibration
   :members:
   :undoc-members:
   :show-inheritance:


Cubic Spline Model
------------------

.. autoclass:: lhcb_ftcalib.BSplineCalibration
   :members:
   :undoc-members:
   :show-inheritance:
