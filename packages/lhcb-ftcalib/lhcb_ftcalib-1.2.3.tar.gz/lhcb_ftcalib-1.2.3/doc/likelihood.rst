Tagging likelihood
==================
In this software package, likelihoods are interpreted in the form of a log-likelihood

Tagging likelihood without mixing
---------------------------------

Tag decisions of a given 
tagging algorithm are "correct" if the tagged flavour :math:`d` is equal to the production
flavour :math:`f_p` and "wrong" otherwise. If a decaying meson can mix before it decays, :math:`f_p` 
needs to be estimated from the time dependent mixing probability of the :math:`B^0` or :math:`B^0_s` meson.
The tagging probability for the simplest case without mixing is given by

.. math::
    \displaystyle\mathcal{L}=\prod_{i,\mathrm{correct}}(1-\omega)\prod_{i,\mathrm{wrong}}\omega,

where :math:`1-\omega` is the tagging probability. This likelihood is used for the calibration of :math:`B^\pm` 
calibration channels.

Tagging likelihood with mixing
------------------------------

If mixing is possible, the flavour at the time of the decay does not necessarily match
the flavour at the time of production. In that case the production flavour is estimated from the predicted production flavour using the time
dependent mixing probability

.. math::
    \displaystyle P(t)=\frac{1}{2}(1-A_{\mathrm{mix}})

whereby

.. math::
    \displaystyle A_{\mathrm{mix}}\approx\frac{\cos(\Delta mt)}{\cosh(\Delta\Gamma t/2)}+\frac{a}{2}\left(1-\frac{\cos^2(\Delta mt)}{\cosh^2(\Delta\Gamma t/2)}\right),

and :math:`a=1-|q/p|^2` which is assumed to be negligible. For events where :math:`A_{\mathrm{mix}}<0`, the production flavour
is assumed to be the inverse flavour and the residual probability that the estimated production flavour is incorrect is then given by

.. math::
    \displaystyle \gamma(t)=\frac{1}{2}(1-|A_{\mathrm{mix}}|).

For simplicity, :math:`\omega(\eta_i,f^{\mathrm{pred}}_i,p_0^+,\ldots p_m^+,p_0^-,\ldots,p_m^-)=\omega_i` and :math:`\gamma(t_i)=\gamma_i` in the following.
Here, :math:`f^{\mathrm{pred}}` denotes the predicted production flavour which is estimated from the decay time and the 
mixing asymmetry: :math:`f^{\mathrm{pred}}_i=\mathrm{sgn}(A_{\mathrm{mix}}(t_i))f^{\mathrm{decay}}_i`. With mixing, the tagging likelihood is given by

.. math::
    \displaystyle\mathcal{L}=\prod_{i,\mathrm{correct}}(1-\gamma_i)(1-\omega_i^{\mathrm{given}})+\gamma_i\omega_i^{\mathrm{opp}}\prod_{i,\mathrm{wrong}}(1-\gamma_i)\omega_i^{\mathrm{given}}+\gamma_i(1-\omega_i^{\mathrm{opp}})),

whereby :math:`\omega^{\mathrm{given}}` is the calibration corresponding to the predicted production flavour :math:`f^{\mathrm{pred}}` and :math:`\omega^{\mathrm{opp}}` is the calibration
function if the predicted production flavour should be the opposite, i.e. :math:`\omega^{\mathrm{opp}}(\eta_i,f^{\mathrm{pred}}_i,\ldots)=\omega^{\mathrm{given}}(\eta_i, -f^{\mathrm{pred}}_i,\ldots)`.
Without mixing, :math:`\gamma(t)=0` and one obtains the tagging likelihood without mixing.


Likelihood gradient
-------------------
In addition, the likelihood gradient is implemented so that the precision of the obtained minimum does not suffer from a lack 
of statistics in the sample. In the following, :math:`L` is assumed to be the negative log-likelihood. It is given by

.. math::
    \displaystyle\nabla L=\sum_{m=0}^{N_p}\frac{\partial L}{\partial p_m}\vec{e}_m,

where the total number of parameters is given by :math:`N_p` and :math:`\vec{e}` is the unit vector. Following the chain rule, the partial derivative
of the log-likelihood with respect to the m-th calibration parameter is given by

.. math::
    \displaystyle\frac{\partial L}{\partial p_m}=\sum_{i,\mathrm{correct}}\frac{\left(\gamma_i\frac{\partial\omega_i^{\mathrm{opp}}}{\partial p_m}-(1-\gamma_i)\frac{\partial\omega_i^{\mathrm{given}}}{\partial p_m}\right)}{(1-\gamma_i)(1-\omega_i^{\mathrm{given}})+\gamma_i\omega_i^{\mathrm{opp}}}
                                               + \sum_{i,\mathrm{wrong}}  \frac{\left((1-\gamma_i)\frac{\partial\omega_i^{\mathrm{given}}}{\partial p_m}-\gamma_i\frac{\partial\omega_i^{\mathrm{opp}}}{\partial p_m}\right)}{(1-\gamma_i)\omega_i^{\mathrm{given}}+\gamma_i(1-\omega_i^{\mathrm{opp}})}

The partial derivative of the chosen calibration function depends on the class of calibration and link function.
