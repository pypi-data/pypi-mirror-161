"""Time parser."""
from typing import Hashable
from typing import Union

import numpy as np
from astropy.time import Time

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import EXP_TIME_ROUND_DIGITS
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud


class TimeBud(UniqueBud):
    """Base class for all Time Buds."""

    def __init__(self, constant_name: str):
        super().__init__(constant_name, metadata_key="time_obs")

    def setter(self, fits_obj: L0FitsAccess) -> Union[float, SpilledDirt]:
        """
        If the file is an observe file, its DATE-OBS value is stored as unix seconds.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The observe time in seconds
        """
        if fits_obj.ip_task_type == "observe":
            return Time(getattr(fits_obj, self.metadata_key), precision=6).unix
        return SpilledDirt


class AverageCadenceBud(TimeBud):
    """Class for the average cadence Bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.average_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the mean cadence between frames.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        The mean value of the cadences of the input frames
        """
        """"""
        return np.mean(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MaximumCadenceBud(TimeBud):
    """Class for the maximum cadence bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.maximum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the maximum cadence between frames.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        The maximum cadence between frames
        """
        return np.max(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MinimumCadenceBud(TimeBud):
    """Class for the minimum cadence bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.minimum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the minimum cadence between frames.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        The minimum cadence between frames
        """
        return np.min(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class VarianceCadenceBud(TimeBud):
    """Class for the variance cadence Bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.variance_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the cadence variance between frames.

        Parameters
        ----------
        key
            The input key
        Returns
        -------
        Return the variance of the cadences over the input frames
        """
        return np.var(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class ExposureTimeFlower(SingleValueSingleKeyFlower):
    """For tagging the frame exposure time.

    Different than SingleValueSingleKeyFlower because we round to avoid jitter in the headers
    """

    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.exposure_time.value, metadata_key="fpa_exposure_time_ms"
        )

    def setter(self, fits_obj: L0FitsAccess):
        """
        Set the exposure time for this flower.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The value of the exposure time
        """
        raw_exp_time = super().setter(fits_obj)
        return round(raw_exp_time, EXP_TIME_ROUND_DIGITS)


class TaskExposureTimesBud(Stem):
    """
    Produce a tuple of all exposure times present in the dataset for a specific ip task type.

    Parameters
    ----------
    stem_name
        The stem name
    ip_task_type
        The ip task type
    """

    def __init__(self, stem_name: str, ip_task_type: str):
        super().__init__(stem_name=stem_name)
        self.metadata_key = "fpa_exposure_time_ms"
        self.ip_task_type = ip_task_type

    def setter(self, fits_obj: L0FitsAccess):
        """
        Set the task exposure time for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The exposure time associated with this fits object
        """
        if fits_obj.ip_task_type.lower() == self.ip_task_type.lower():
            raw_exp_time = getattr(fits_obj, self.metadata_key)
            return round(raw_exp_time, EXP_TIME_ROUND_DIGITS)
        return SpilledDirt

    def getter(self, key: Hashable) -> Hashable:
        """
        Get the list of exposure times.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        exp_time_tup = tuple(sorted(set(self.key_to_petal_dict.values())))
        return exp_time_tup
