"""
Components of the Constant model.

Contains names of database entries and Base class for an object that simplifies
accessing the database (tab completion, etc.)
"""
from enum import Enum
from string import ascii_uppercase
from typing import List

from hashids import Hashids

from dkist_processing_common._util.constants import ConstantsDb


class BudName(str, Enum):
    """Controlled list of names for constant stems (buds)."""

    recipe_run_id = "RECIPE_RUN_ID"
    instrument = "INSTRUMENT"
    num_cs_steps = "NUM_CS_STEPS"
    num_modstates = "NUM_MODSTATES"
    proposal_id = "PROPOSAL_ID"
    average_cadence = "AVERAGE_CADENCE"
    maximum_cadence = "MAXIMUM_CADENCE"
    minimum_cadence = "MINIMUM_CADENCE"
    variance_cadence = "VARIANCE_CADENCE"
    num_dsps_repeats = "NUM_DSPS_REPEATS"
    spectral_line = "SPECTRAL_LINE"
    dark_exposure_times = "DARK_EXPOSURE_TIMES"


class ConstantsBase:
    """
    Aggregate (from the constant flowers flower pot) in a single property on task classes.

    It also provides some default constants, but is intended to be subclassed by instruments.

    To subclass:

    1. Create the actual subclass. All you need to do is add more @properties for the constants you want

    2. Update the instrument class's `constants_model_class` property to return the new subclass. For example::

         class NewConstants(ConstantsBase):
            @property
            def something(self):
                return 7

         class InstrumentWorkflowTask(WorkflowTaskBase):
            @property
            def constants_model_class:
                return NewConstants

            ...

    Parameters
    ----------
    recipe_run_id
        Thew recipe_run_id
    task_name
        The task_name
    """

    def __init__(self, recipe_run_id: int, task_name: str):
        self._db_dict = ConstantsDb(recipe_run_id=recipe_run_id, task_name=task_name)
        self._recipe_run_id = recipe_run_id

    # These management functions are all underscored because we want tab-complete to *only* show the available
    #  constants
    def _update(self, d: dict):
        self._db_dict.update(d)

    def _purge(self):
        self._db_dict.purge()

    def _close(self):
        self._db_dict.close()

    @property
    def dataset_id(self) -> str:
        """Define the dataset_id constant."""
        return Hashids(min_length=5, alphabet=ascii_uppercase).encode(self._recipe_run_id)

    @property
    def proposal_id(self) -> str:
        """Get the proposal_id constant."""
        return self._db_dict[BudName.proposal_id]

    @property
    def instrument(self) -> str:
        """Get the instrument name."""
        return self._db_dict[BudName.instrument]

    @property
    def average_cadence(self) -> float:
        """Get the average_cadence constant."""
        return self._db_dict[BudName.average_cadence]

    @property
    def maximum_cadence(self) -> float:
        """Get the maximum cadence constant constant."""
        return self._db_dict[BudName.maximum_cadence]

    @property
    def minimum_cadence(self) -> float:
        """Get the minimum cadence constant constant."""
        return self._db_dict[BudName.minimum_cadence]

    @property
    def variance_cadence(self) -> float:
        """Get the variance of the cadence constant."""
        return self._db_dict[BudName.variance_cadence]

    @property
    def num_dsps_repeats(self) -> int:
        """Get the number of dsps repeats."""
        return self._db_dict[BudName.num_dsps_repeats]

    @property
    def spectral_line(self) -> str:
        """Get the spectral line for this task."""
        return self._db_dict[BudName.spectral_line]

    @property
    def dark_exposure_times(self) -> List[float]:
        """Get a list of exposure times used in the dark calibration."""
        return self._db_dict[BudName.dark_exposure_times]

    @property
    def stokes_params(self) -> [str]:
        """Return the list of stokes parameter names."""
        return ["I", "Q", "U", "V"]
