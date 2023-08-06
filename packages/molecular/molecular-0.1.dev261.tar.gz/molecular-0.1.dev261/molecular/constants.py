"""
Boltzmann
"""

import numpy as np

from scipy.constants import Boltzmann, Avogadro, atmosphere
import scipy.constants

__all__ = [
    'AVOGADRO',
    'BOLTZMANN'
]


# Unit class
class Unit:
    def __init__(self, symbol):
        self.magnitude = ''
        self.symbol = symbol
        self.inverse = False

    def __repr__(self):
        return self.to_string()

    def __truediv__(self, other):
        u = ComplexUnit()
        u.add(self)
        u.add(other.invert())
        return u

    def copy(self):
        u = Unit(symbol=self.symbol)
        u.magnitude = self.magnitude
        u.inverse = self.inverse
        return u

    def invert(self):
        u = self.copy()
        u.inverse = True
        return u

    def to_string(self, ignore_inverse=True):
        repr = self.magnitude + self.symbol
        if not ignore_inverse and self.inverse:
            repr = f'1 / {repr}'
        return repr


class ComplexUnit:
    def __init__(self):
        self._units = []

    def __repr__(self):
        num = []
        den = []
        for unit in self._units:
            repr = unit.to_string(ignore_inverse=True)
            if unit.inverse:
                den.append(repr)
            else:
                num.append(repr)
        num_str = '*'.join(num)
        den_str = '*'.join(den)
        if len(num) > 1:
            num_str = f'({num_str})'
        if len(den) > 1:
            den_str = f'({den_str})'
        if len(num) == 0:
            num_str = '1'
        if len(den) > 0:
            return f'{num_str}/{den_str}'
        else:
            return num_str

    def add(self, unit):
        self._units.append(unit)


# Define base units
ANGSTROM = Unit(symbol='Å')
SECOND = Unit(symbol='s')

# Define



AVOGADRO = 6.02214076e23  # scipy.constants.Avogadro
BOLTZMANN = 1.380649e-23  # scipy.constants.Boltzmann
CAL_TO_JOULE = 4.184  # 1 calorie = 4.184 joules
KCAL_TO_JOULE = CAL_TO_JOULE * 1000.


# TODO make this easily usable.
class GasConstant:
    def __init__(self):
        pass

    @property
    def kcal_per_K_mol(self):
        return per_mole(joule_to_kcal(BOLTZMANN))


# Joule to kcal conversion
def joule_to_kcal(x):
    """
    Convert joule to kcal. 1 J = 1 / 4184. kcal

    Parameters
    ----------
    x : float
        Joule.

    Returns
    -------
    float
        kcal.
    """

    return x / 4184.


# kcal to Joule conversion
def kcal_to_joule(x):
    """
    Convert kcal to joule. 1 kcal = 4184 J.

    Parameters
    ----------
    x : float
        kcal.

    Returnsx
    -------
    float
        Joule.
    """

    return 4184. * x


def per_mole(x):
    """
    Convert quantity to per mole. Divide by NA.

    Parameters
    ----------
    x : float
        Quantity.

    Returns
    -------
    float
        Quantity per mole.
    """

    return x * AVOGADRO


class Quantity:
    def __init__(self, value, units=None):
        self._value = value
        if units is None:
            units = Unit
        self._units = units

    def __repr__(self):
        return f'{self._value} {self._units.symbol}'


# Boltzmann constant in kcal/K/mol
BOLTZMANN_KCAL_K_MOL = per_mole(joule_to_kcal(BOLTZMANN))
BOLTZMANN_KCAL_MOL_K = BOLTZMANN_KCAL_K_MOL
np.testing.assert_almost_equal(BOLTZMANN * AVOGADRO / 4184., BOLTZMANN_KCAL_K_MOL)

# Pressure
pressure = Avogadro * atmosphere / 1e30 / 4184.  # 1e-30 m^3 per A^3, 4184 J per kcal

if __name__ == '__main__':
    x = Quantity(100, units=ANGSTROM)
    print(f'kb={BOLTZMANN_KCAL_MOL_K} kcal/mol')
