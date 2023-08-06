"""
Builder for the snapshot from smaller snapshots.
"""
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import VectorQuantity

from omtool.core.datamodel import Snapshot


class SnapshotBuilder:
    """
    Builder for the snapshot from smaller snapshots.
    """

    def __init__(self):
        self.snapshot = Snapshot(Particles(), 0 | units.Myr)

    def add_snapshot(
        self,
        snapshot: Snapshot,
        offset: VectorQuantity = [0, 0, 0] | units.kpc,
        velocity: VectorQuantity = [0, 0, 0] | units.kms,
    ):
        """
        Appends snapshot of any number of particles to the result.
        """
        snapshot.particles.position += offset
        snapshot.particles.velocity += velocity

        self.snapshot = self.snapshot + snapshot

    def add_particles(self, particles: Particles):
        """
        Appends particles to the result and takes timestamp from it.
        """
        self.snapshot.particles.add_particles(particles)

    def get_result(self) -> Snapshot:
        """
        Returns resulting snapshot.
        """
        self.snapshot.particles.move_to_center()

        return self.snapshot

    def to_fits(self, filename: str):
        """
        Writes reult to FITS file.
        """
        self.snapshot.particles.move_to_center()
        self.snapshot.to_fits(filename)
