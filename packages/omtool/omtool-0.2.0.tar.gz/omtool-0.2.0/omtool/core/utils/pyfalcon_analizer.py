from collections import namedtuple
from functools import lru_cache

import pyfalcon
from amuse.lab import Particles, ScalarQuantity, VectorQuantity, units

Units = namedtuple("Units", "L V M T")
u = Units(L=units.kpc, M=232500 * units.MSun, T=units.Gyr, V=units.kms)

ScalarQuantity.__hash__ = lambda q: hash((q.number, q.unit))


@lru_cache(maxsize=10)
def get_potentials(particles: Particles, eps: ScalarQuantity) -> VectorQuantity:
    pos = particles.position.value_in(u.L)
    mass = particles.mass.value_in(u.M)
    eps = eps.value_in(u.L)

    _, pot = pyfalcon.gravity(pos, mass, eps)

    return pot | u.L**2 / u.T**2
