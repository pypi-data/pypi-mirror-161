Tagger combination
==================

The combination of multiple tag decision :math:`d_i` and mistag estimates :math:`\omega_i (\eta_i)` is calculated by building the probability :math:`P_b` (:math:`P_\overline{b}`)
for a signal candidate to contain a :math:`b` (:math:`\overline{b}`) quark via

.. math::
    \displaystyle P_b( p_b,  p_\overline{b}) = \frac{p_b}{p_b + p_\overline{b}} \quad\mathrm{and}\quad P_\overline{b} = 1 - P_b

Here, :math:`p` combines the tagging algorithms like

.. math::
    \displaystyle p_b(\vec{\omega}, \vec{d})                              & = & \prod_i\left(\frac{1 + d_i}{2} - d_i\left(1-\omega_i(\eta_i)\right)\right)\ , \\
    \displaystyle \quad\mathrm{and}\quad p_\overline{b}(\vec{\omega}, \vec{d}) & = & \prod_i\left(\frac{1 - d_i}{2} + d_i\left(1-\omega_i(\eta_i)\right)\right)\ ,

while the combined tag decision and mistag estimate are calculated via

.. math::
    \displaystyle d_\text{comb}                    = \text{sign}\left(P_b-P_\overline{b}\right)\ ,
    \displaystyle \text{and}\qquad\eta_\text{comb} = 1 - \max\left(P_b, P_\overline{b}\right)\ .


Error propagation
-----------------
Uncertainties of input parameters :math:`\vec{x}` of a function :math:`\vec{f}(\vec{x})` can be propgated in the form

.. math::
    \displaystyle C_f = J_f \cdot C_x \cdot J_f^\mathrm{T}

where :math:`C_x` denotes the covariance matrix of :math:`\vec{x}` and :math:`J_f` the Jacobian matrix of :math:`\vec{f}(\vec{x})` .

The (optional) propgation of calibration uncertainties through the highly non-linear combination algorithm exploits the fact, that the uncertainty of :math:`\eta_\mathrm{comb}` equals the uncertainty  :math:`P_b` indpendent of the combined tag decision, since :math:`P_b = P_\overline{b}`.

The propagation can be followed most easily when the individual combination steps are spectated. So the covariance of :math:`P_b` (and :math:`\eta_\mathrm{comb}` ) is given by

.. math::
    \displaystyle C_\mathrm{comb} = (J_P \cdot J_p \cdot J_\omega) \cdot C_\omega \cdot (J_P \cdot J_p \cdot J_\omega)^\mathrm{T},

where :math:`J_P` is the Jacobian matrix of :math:`P_b( p_b,  p_\overline{b})`

.. math::
    \displaystyle J_P = \begin{bmatrix}\frac{p_\overline{b}}{(p_b + p_\overline{b})^2} \\ \frac{p_b}{(p_b + p_\overline{b})^2} \end{bmatrix},

with dimension :math:`1 \times 2`. :math:`J_p` is the Jacobian matrix of :math:`\vec{p}(\vec{\omega}) = ( \begin{bmatrix} p_b(\vec{\omega}), &  p_\overline{b}(\vec{\omega})\end{bmatrix})`

.. math::
    \displaystyle J_p = \begin{bmatrix}\prod_i \left( \frac{1 + d_i}{2} - d_i(1-\omega_i), \,\mathrm{if}\, i\neq 1 \,\mathrm{else}\, d_i \right) & \prod_i \left( \frac{1 - d_i}{2} + d_i(1-\omega_i), \,\mathrm{if}\, i\neq 1 \,\mathrm{else}\, -d_i \right) \\
    \vdots & \vdots \\ \prod_i \left( \frac{1 + d_i}{2} - d_i(1-\omega_i), \,\mathrm{if}\, i\neq N_\mathrm{T} \,\mathrm{else}\, d_i \right) & \prod_i \left( \frac{1 - d_i}{2} + d_i(1-\omega_i), \,\mathrm{if}\, i\neq N_\mathrm{T} \,\mathrm{else}\, -d_i \right)\end{bmatrix},

with dimension :math:`2 \times N_\mathrm{T}`, where :math:`N_\mathrm{T}` is the number of taggers included in the combination.

:math:`J_\omega` is the Jacobian matrix of :math:`\vec{\omega} (\vec{\eta}; \vec{q}))`

.. math::
    \displaystyle J_\omega = \begin{bmatrix}\frac{\partial\omega_1}{\partial q_1} & \cdots & \frac{\partial\omega_1}{\partial q_i} \\ \vdots & \ddots & \vdots \\ \frac{\partial\omega_j}{\partial q_1} & \cdots & \frac{\partial\omega_j}{\partial q_i}\end{bmatrix}

with dimension :math:`N_\mathrm{T} \times N_\mathrm{pars}`, where :math:`N_\mathrm{pars}` is the summed number of calibration parameters of all taggers included in the combination.

Last, the covariance matrix :math:`C_\omega` is a diagonal block matrix of the individual taggers' calibration covariances

.. math::
    \displaystyle J_\omega = \begin{bmatrix}C_{\omega_1} &  & 0 \\  & \ddots &  \\ 0 &  & C_{\omega_{N_\mathrm{T}}}\end{bmatrix}.

The (block) dimension of the covariance matirx is :math:`N_\mathrm{pars} \times N_\mathrm{pars}` (:math:`N_\mathrm{T} \times N_\mathrm{T}` ). The diagonality is given by the independence of the calibrations of individual taggers.

Due to the :math:`1 \times 2` dimension of the :math:`J_P` matrix the dimension of the resulting covariance :math:`C_\mathrm{comb}` is :math:`1 \times 1` , which allows to obtain the uncertainty :math:`\Delta\eta_\mathrm{comb} = \sqrt{C_\mathrm{comb}}` .

The combination has to proceed event wise. This makes the combination computationaly expensive. To avoid unecessary overhead the error propagtion within the combination algorithm is optional. If necessary, it can be enabled by the commandline argument ``-propagate_errors`` or by the :doc:`global options<GlobalOptions>` flag ``propagate_errors`` . 