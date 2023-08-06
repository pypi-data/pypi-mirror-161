"""
Provides methods to load the set of snapshots from FITS and other
types of files.
"""
from typing import Iterator, Tuple

from amuse.lab import Particles, ScalarQuantity

from omtool.io_service import readers
from omtool.io_service.config import IOServiceConfig


class InputService:
    """
    Provides methods to load the set of snapshots from FITS and other
    types of files.
    """

    def __init__(self, config: IOServiceConfig) -> None:
        self.config = config

    def get_snapshot_generator(self) -> Iterator[Tuple[Particles, ScalarQuantity]]:
        """
        Loads the snapshot from the file and adds an ability to read next snapshot.
        Implementation IS lazy.
        """
        if self.config.format == "fits":
            if len(self.config.filenames) > 1:
                raise NotImplementedError(
                    "Reading of multiple FITS files at once is not implemented yet."
                )

            return readers.from_fits(self.config.filenames[0])
        elif self.config.format == "csv":
            return readers.from_logged_csvs(self.config.filenames)
        else:
            raise RuntimeError(f'Unknown format of the file: "{self.config.format}"')

    def get_number_of_snapshots(self) -> int:
        """
        Returns number of snapshots in a given file. It is much faster than
        lazily iterate over all of them.
        """
        if self.config.format == "fits":
            if len(self.config.filenames) > 1:
                raise NotImplementedError(
                    "Reading of multiple FITS files at once is not implemented yet."
                )

            return readers.fits_file_info(self.config.filenames[0])
        elif self.config.format == "csv":
            raise NotImplementedError("Length of list of csv snapshots is not implemented yet.")
        else:
            raise RuntimeError(f'Unknown format of the file: "{self.config.format}"')
