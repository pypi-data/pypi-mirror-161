"""
statistics.py

author: C. Lockhart <clockha2@gmu.edu>
language: Python3
"""

from scipy.stats import sem as _sem


# Compute SEM
def sem(a, *args, **kwargs):
    r"""
    Compute standard error of mean, :math:`\delta_M`. See :ref:`scipy.stats.sem`.

    .. math::

       \delta_{M} = \frac{\sqrt{\frac{1}{n-1} \sum_{i=1}^n (x(i) - \mu_x)^2}}{\sqrt{n}}

    This is equivalent to np.std(a, ddof=1) / np.sqrt(len(a))
    """

    return _sem(a, *args, **kwargs)

