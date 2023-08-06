import numpy as np
from amuse.lab import units

from omtool.core.datamodel import Snapshot


def get_galactic_basis(snapshot: Snapshot):
    particles = snapshot.particles
    r = particles.position.value_in(units.kpc)
    v = particles.velocity.value_in(units.kms)
    cm = particles.center_of_mass().value_in(units.kpc)
    cm_vel = particles.center_of_mass_velocity().value_in(units.kms)
    m = particles.mass.value_in(units.MSun)

    r = r - cm
    v = v - cm_vel
    L = m[:, np.newaxis] * np.cross(v, r)
    e1 = np.sum(L, axis=0)
    e1 = e1 / (e1**2).sum() ** 0.5

    e2 = np.empty(e1.shape)
    e2[0] = 1
    e2[1] = 0
    e2[2] = -e2[0] * e1[0] / e1[2] - e2[1] * e1[1] / e1[2]
    e2 = e2 / (e2**2).sum() ** 0.5

    e3 = np.cross(e1, e2)

    return (e1, e2, e3)
