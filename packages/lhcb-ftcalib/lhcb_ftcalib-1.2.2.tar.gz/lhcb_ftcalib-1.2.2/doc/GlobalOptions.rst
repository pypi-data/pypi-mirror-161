Global Options
==============

A set of global options is available for the user to adjust. It is important to
adjust constants `before` doing anything else, otherwise changing these
constants will have no effect.

Example use
***********
.. code-block:: python

   import lhcb_ftcalib as ft

   ft.constants.DeltaGamma_d = 0.0002  # Future value?

   tagger = ft.Tagger(...)
   
   print(tagger.DeltaGamma)  # -> 0.0002


List of global options
**********************

* ``DeltaM_d`` (default: HFLAV 2021)
    * Oscillation frequency :math:`\Delta m_d`
* ``DeltaGamma_d`` (default: HFLAV 2021)
    * Decay width difference :math:`\Delta\Gamma_d`
* ``DeltaM_s`` (default: HFLAV 2021)
    * Oscillation frequency :math:`\Delta m_s`
* ``DeltaGamma_s`` (default: HFLAV 2021)
    * Decay width difference :math:`\Delta\Gamma_s`
* ``propagate_errors`` (default: False)
    * If true, errors are propagated in combination algorithm. Details on the combination algorithm and its error propagation can be found :doc:`here <combination>`
* ``calculate_omegaerr`` (default: True)
    * If true, mistag uncertainty is computed for calibration with given parameter uncertainties
* ``ignore_mistag_asymmetry_for_apply`` (default: True)
    * If true, averaged calibration is written to tuple instead of flavour specific calibration
* ``CovarianceCorrectionMethod``
    For calibrations with per-event weights, multiple methods are available to correct
    the covariance matrix in order to reflect the statistics of the underlying information.

    * ``"SquaredHesse"`` **(default)**

         The covariance matrix :math:`C'` is computed from a modified Hessian :math:`\tilde{H}`.

        :math:`C'=-C \tilde{H} C`

        :math:`\displaystyle\tilde{H}=\displaystyle\sum_i w_i^2\begin{bmatrix}
        \left.\frac{\partial^2\mathcal{L}}{\partial\theta_0^2}\right\vert_{\eta=\eta_i} & \cdots & \left.\frac{\partial^2\mathcal{L}}{\partial\theta_0\partial\theta_n}\right\vert_{\eta=\eta_i} \\
        \vdots & \ddots & \vdots \\
        \left.\frac{\partial^2\mathcal{L}}{\partial\theta_n\partial\theta_0}\right\vert_{\eta=\eta_i} & \cdots & \left.\frac{\partial^2\mathcal{L}}{\partial\theta_n^2}\right\vert_{\eta=\eta_i}
        \end{bmatrix}`

        The covariance matrix in this case is 

        :math:`C = -H^{-1}`

        and the weighted hessian :math:`H` is computed via

        :math:`\displaystyle H=\displaystyle\sum_i w_i\begin{bmatrix}
        \left.\frac{\partial^2\mathcal{L}}{\partial\theta_0^2}\right\vert_{\eta=\eta_i} & \cdots & \left.\frac{\partial^2\mathcal{L}}{\partial\theta_0\partial\theta_n}\right\vert_{\eta=\eta_i} \\
        \vdots & \ddots & \vdots \\
        \left.\frac{\partial^2\mathcal{L}}{\partial\theta_n\partial\theta_0}\right\vert_{\eta=\eta_i} & \cdots & \left.\frac{\partial^2\mathcal{L}}{\partial\theta_n^2}\right\vert_{\eta=\eta_i}
        \end{bmatrix}`

        Where :math:`\mathcal{L}=\mathcal{L}(\eta, d;\vec{\theta})` is the tagging log-likelihood.
    * ``"SumW2"``

      * The covariance matrix is scaled by a factor: :math:`C'=C\sum w_i/\sum w_i^2`
    * ``"None"``

      * No scaling is applied. (Obviously not recommended)

