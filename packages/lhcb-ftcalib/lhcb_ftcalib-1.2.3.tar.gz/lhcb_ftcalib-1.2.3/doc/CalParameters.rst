Calibration Parameter Conventions
=================================

Internally, ftcalib uses multiple different conventions
for representing calibration parameters. The class CalParameters
is used to convert between these representations.

The "delta"-parameter convention is most widely used to report a calibration. Is is of the form

:math:`\vec{\Theta}^\Delta = \{p_0,\cdots,p_n,\Delta p_0,\cdots,\Delta p_n\}`

for a calibration of degree :math:`n`. Here, the :math:`\Delta p_i` represent the difference of the 
calibrations for the predicted :math:`B` and :math:`\overline{B}` flavours.

The flavour-specific convention is used internally
because of its symmetric properties for both predicted production flavours and therefore
better compatibility to the Flavour Tagging Likelihood.

:math:`\vec{\Theta}^\pm = \{p_0^+,\cdots,p_n^+,p_0^-,\cdots,p_n^-\}`

Finally, a flavour-averaged representation is used specifically for estimating the 
uncertainty on some performance numbers like the tagging power that is due to the chosen calibration model.

:math:`\vec{\overline{\Theta}} = \{p_0,\cdots,p_n\}`

The relationship between the "delta" and the "flavour" convention is

:math:`\displaystyle\begin{bmatrix}\frac{1}{2}\mathbb{1}_{n} & \frac{1}{2}\mathbb{1}_{n}\\\mathbb{1}_{n} & -\mathbb{1}_{n} \end{bmatrix}\vec{\Theta}^\pm=\vec{\Theta}^\Delta`,
i.e. :math:`\qquad p_i = \frac{1}{2}(p_i^++p_i^-)`, :math:`\Delta p_i = p_i^+-p_i^-`

and

:math:`\displaystyle\begin{bmatrix}\mathbb{1}_{n} & \frac{1}{2}\mathbb{1}_{n}\\\mathbb{1}_{n} & -\frac{1}{2}\mathbb{1}_{n} \end{bmatrix}\vec{\Theta}^\Delta=\vec{\Theta}^\pm`
i.e. :math:`\qquad\displaystyle p_i^\pm = \left(p_i\pm\frac{\Delta p_i}{2}\right)`

.. autoclass:: CalParameters.CalParameters
   :members:
   :undoc-members:
   :show-inheritance:
