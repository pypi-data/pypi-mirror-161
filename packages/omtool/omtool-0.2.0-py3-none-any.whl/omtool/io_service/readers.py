"""
Functions to read different types of files and load them into snapshots.
"""
from typing import Iterator, List, Tuple

import numpy as np
import pandas
from amuse.lab import Particle, Particles, ScalarQuantity, units
from astropy.io import fits
from astropy.io.fits.hdu.table import BinTableHDU

fields = {
    "x": units.kpc,
    "y": units.kpc,
    "z": units.kpc,
    "vx": units.kms,
    "vy": units.kms,
    "vz": units.kms,
    "mass": units.MSun,
    "is_barion": None,
}


def from_logged_csvs(
    filenames: List[str], delimiter: str = ","
) -> Iterator[Tuple[Particles, ScalarQuantity]]:
    """
    Loads snapshots from csv file in the following form: T,x,y,z,vx,vy,vz

    Implementation is not lazy, iterators exist only for the convinience.
    """
    tables = [
        pandas.read_csv(filename, delimiter=delimiter, index_col=False).iterrows()
        for filename in filenames
    ]

    for rows in zip(*tables):
        rows = [row for (_, row) in rows]

        particles = Particles()

        for row in rows:
            particle = Particle()
            # probably need to use fields dict
            particle.position = [row["x"], row["y"], row["z"]] | units.kpc
            particle.velocity = [row["vx"], row["vy"], row["vz"]] | units.kms
            particle.mass = row["m"] | units.MSun
            particle.is_barion = 1

            particles.add_particle(particle)

        yield particles, rows[0]["T"] | units.Myr


def from_fits(filename: str) -> Iterator[Tuple[Particles, ScalarQuantity]]:
    """
    Loads snapshots from the FITS file where each HDU stores binary table with one timestamp.
    """
    hdul = fits.open(filename, memmap=True)

    for frame in range(len(hdul) - 1):
        table: BinTableHDU = hdul[frame + 1]
        number_of_particles = len(table.data[list(fields.keys())[0]])

        timestamp = table.header["TIME"] | units.Myr
        particles = Particles(number_of_particles)

        for (key, val) in fields.items():
            if val is not None:
                setattr(particles, key, table.data[key] | val)
            else:
                data = np.array(table.data[key], dtype=np.float64)
                setattr(particles, key, data)

        yield particles, timestamp


def fits_file_info(filename: str) -> int:
    """
    Returns number of snapshots in the FITS file.
    """
    hdul = fits.open(filename, memmap=True)

    number_of_snaps = len(hdul) - 1

    hdul.close()

    return number_of_snaps
