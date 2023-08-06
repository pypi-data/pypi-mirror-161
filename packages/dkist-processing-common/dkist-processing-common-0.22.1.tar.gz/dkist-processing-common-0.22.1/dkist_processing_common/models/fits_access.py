"""Abstraction layer for accessing fits data via class attributes."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
from typing import Union

import numpy as np
from astropy.io import fits


class FitsAccessBase:
    """
    Abstraction layer for accessing fits data via class attributes.

    Parameters
    ----------
    hdu
        The fits object
    name
        An optional name that can be associated with the object
    auto_squeeze
        A boolean indicating whether to 'squeeze' out dimensions of size 1
    """

    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: bool = True,
    ):
        self._hdu = hdu
        self.name = name
        self.auto_squeeze = auto_squeeze

    @property
    def data(self) -> np.ndarray:
        """
        Return the data array from the associated FITS object, with axes of length 1 removed if the array has three dimensions and the unit axis is the zeroth one.

        This is intended solely to remove the dummy dimension that is in raw data from the summit.

        Setting `auto_squeeze = False` when initializing this object will never squeeze out any dimensions

        Returns
        -------
        data array
        """
        # This conditional is explicitly to catch summit data with a dummy first axis for WCS
        # purposes
        if self.auto_squeeze and len(self._hdu.data.shape) == 3 and self._hdu.data.shape[0] == 1:
            return np.squeeze(self._hdu.data)
        return self._hdu.data

    @data.setter
    def data(self, array: np.ndarray) -> None:
        """
        Set the data array using an input data array.

        Parameters
        ----------
        array
            The input array

        Returns
        -------
        None
        """
        # There is no shape magic stuff going on here right now because the tasks/services that care about
        # it will deal with it themselves (I think (tm)).
        self._hdu.data = array

    @property
    def header(self) -> fits.Header:
        """Return the header for this fits object."""
        return self._hdu.header

    @property
    def size(self) -> float:
        """Return the size in bytes of the data portion of this fits object."""
        return self._hdu.size

    @classmethod
    def from_header(
        cls, header: Union[fits.Header, dict], name: Optional[str] = None
    ) -> FitsAccessBase:
        """
        Convert a header to a CommonFitsData (or child) object.

        Parameters
        ----------
        header
            A single `astropy.io.fits.header.Header` HDU object.
        name
            A unique name for the fits access instance
        """
        if isinstance(header, dict):
            header = fits.Header(header)
        hdu = fits.PrimaryHDU(header=header)
        return cls(hdu=hdu, name=name)

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> FitsAccessBase:
        """
        Load the file at given path into a FitsAccess object.

        Parameters
        ----------
        path
            Location of fits file on disk
        """
        hdul = fits.open(path)
        if hdul[0].data is not None:
            hdu = hdul[0]
        else:
            hdu = hdul[1]
        return cls(hdu=hdu, name=path)
