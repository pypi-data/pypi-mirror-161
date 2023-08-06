"""
Global test fixtures
"""
import json
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from random import randint
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from uuid import uuid4

import numpy as np
import pytest
from astropy import coordinates
from astropy.io import fits
from astropy.time import Time
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator
from dkist_header_validator.translator import sanitize_to_spec214_level1
from dkist_processing_pac.fitter.fitter_parameters import PolcalDresserParameters
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.drawer import Drawer
from dkist_processing_pac.input_data.dresser import Dresser
from dkist_processing_pac.optics.calibration_unit import CalibrationUnit
from dkist_processing_pac.optics.telescope import Telescope

from dkist_processing_common._util.constants import ConstantsDb
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common._util.tags import TagDB
from dkist_processing_common.models.graphql import InputDatasetResponse
from dkist_processing_common.models.graphql import RecipeInstanceResponse
from dkist_processing_common.models.graphql import RecipeRunResponse
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin

TILE_SIZE = 64


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


@pytest.fixture()
def tag_db(recipe_run_id) -> TagDB:
    t = TagDB(recipe_run_id=recipe_run_id, task_name="test_tags")
    yield t
    t.purge()
    t.close()


@pytest.fixture()
def tag_db2(recipe_run_id) -> TagDB:
    """
    Another instance of a tag db in the same redis db
    """
    recipe_run_id = recipe_run_id + 15  # same db number but different namespace
    t = TagDB(recipe_run_id=recipe_run_id, task_name="test_tags2")
    yield t
    t.purge()
    t.close()


@pytest.fixture(params=[None, "use_tmp_path"])
def workflow_file_system(request, recipe_run_id, tmp_path) -> Tuple[WorkflowFileSystem, int, Path]:
    if request.param == "use_tmp_path":
        path = tmp_path
    else:
        path = request.param
    wkflow_fs = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        task_name="wkflow_fs_test",
        scratch_base_path=path,
    )
    yield wkflow_fs, recipe_run_id, tmp_path
    wkflow_fs.purge(ignore_errors=True)
    tmp_path.rmdir()
    wkflow_fs.close()


@pytest.fixture()
def constants_db(recipe_run_id) -> ConstantsDb:
    constants = ConstantsDb(recipe_run_id=recipe_run_id, task_name="test_constants")
    yield constants
    constants.purge()
    constants.close()


class CommonDataset(Spec122Dataset):
    def __init__(self):
        super().__init__(
            array_shape=(1, 10, 10),
            time_delta=1,
            dataset_shape=(2, 10, 10),
            instrument="visp",
            start_time=datetime(2020, 1, 1, 0, 0, 0, 0),
        )

        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("TAZIMUTH", 3.14)
        self.add_constant_key("TTBLANGL", 1.23)
        self.add_constant_key("INST_FOO", "bar")
        self.add_constant_key("DKIST004", "observe")
        self.add_constant_key("ID___005", "ip id")
        self.add_constant_key("PAC__004", "Sapphire Polarizer")
        self.add_constant_key("PAC__005", "31.2")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "6.66")
        self.add_constant_key("PAC__008", "DarkShutter")
        self.add_constant_key("INSTRUME", "VISP")
        self.add_constant_key("WAVELNTH", 1080.0)
        self.add_constant_key("DATE-OBS", "2020-01-02T00:00:00.000000")
        self.add_constant_key("DATE-END", "2020-01-03T00:00:00.000000")
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("BZERO", 0)
        self.add_constant_key("BSCALE", 1)


@pytest.fixture()
def complete_common_header():
    """
    A header with some common by-frame keywords
    """
    ds = CommonDataset()
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    return header_list[0]


@pytest.fixture()
def complete_l1_only_header(complete_common_header):
    """
    A header with only 214 L1 keywords
    """
    complete_common_header["DAAXES"] = 1
    complete_common_header["DEAXES"] = 1
    complete_common_header["DNAXIS"] = 2
    l1_header = sanitize_to_spec214_level1(complete_common_header)

    return l1_header


class CalibrationSequenceDataset(Spec122Dataset):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        time_delta: float,
        instrument="visp",
    ):
        self.num_frames_per_CS_step = 5

        # Make up a Calibration sequence. Mostly random except for two clears and two darks at start and end, which
        # we want to test
        self.pol_status = [
            "clear",
            "clear",
            "Sapphire Polarizer",
            "Fused Silica Polarizer",
            "Sapphire Polarizer",
            "clear",
            "clear",
        ]
        self.pol_theta = ["0.0", "0.0", "60.0", "60.0", "120.0", "0.0", "0.0"]
        self.ret_status = ["clear", "clear", "clear", "SiO2 SAR", "clear", "clear", "clear"]
        self.ret_theta = ["0.0", "0.0", "0.0", "45.0", "0.0", "0.0", "0.0"]
        self.dark_status = [
            "DarkShutter",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "DarkShutter",
        ]

        self.num_steps = len(self.pol_theta)
        dataset_shape = (self.num_steps * self.num_frames_per_CS_step,) + array_shape[1:]
        super().__init__(
            dataset_shape,
            array_shape,
            time_delta,
            instrument=instrument,
            start_time=datetime(2020, 1, 1, 0, 0, 0),
        )
        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")

    @property
    def cs_step(self) -> int:
        return self.index // self.num_frames_per_CS_step

    @key_function("PAC__004")
    def polarizer_status(self, key: str) -> str:
        return self.pol_status[self.cs_step]

    @key_function("PAC__005")
    def polarizer_angle(self, key: str) -> str:
        return str(self.pol_theta[self.cs_step])

    @key_function("PAC__006")
    def retarder_status(self, key: str) -> str:
        return self.ret_status[self.cs_step]

    @key_function("PAC__007")
    def retarder_angle(self, key: str) -> str:
        return str(self.ret_theta[self.cs_step])

    @key_function("PAC__008")
    def gos_level3_status(self, key: str) -> str:
        return self.dark_status[self.cs_step]


class NonPolCalDataset(Spec122Dataset):
    def __init__(self):
        super().__init__(
            dataset_shape=(4, 2, 2),
            array_shape=(1, 2, 2),
            time_delta=1,
            instrument="visp",
            start_time=datetime(2020, 1, 1, 0, 0, 0),
        )  # Instrument doesn't matter
        self.add_constant_key("DKIST004", "dark")  # Anything that's not polcal
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")
        self.add_constant_key("PAC__004", "clear")
        self.add_constant_key("PAC__005", "0.0")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("PAC__008", "DarkShutter")


@pytest.fixture(scope="session")
def grouped_cal_sequence_headers() -> Dict[int, List[L0FitsAccess]]:
    ds = CalibrationSequenceDataset(array_shape=(1, 2, 2), time_delta=2.0)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]
    expected_cs_dict = defaultdict(list)
    for i in range(ds.num_steps):
        for j in range(ds.num_frames_per_CS_step):
            expected_cs_dict[i].append(L0FitsAccess.from_header(header_list.pop(0)))

    return expected_cs_dict


@pytest.fixture(scope="session")
def non_polcal_headers() -> List[L0FitsAccess]:
    ds = NonPolCalDataset()
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]
    obj_list = [L0FitsAccess.from_header(h) for h in header_list]
    return obj_list


@pytest.fixture(scope="session")
def max_cs_step_time_sec() -> float:
    """Max CS step time in seconds"""
    return 20.0


class InputDatasetTask(WorkflowTaskBase, InputDatasetMixin):
    def run(self):
        pass


@pytest.fixture
def construct_task_with_input_dataset(tmp_path, recipe_run_id):
    def construct_task(input_dataset_dict):
        with InputDatasetTask(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        ) as task:
            task.scratch = WorkflowFileSystem(
                recipe_run_id=recipe_run_id,
                scratch_base_path=tmp_path,
            )
            task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
            file_path = task.scratch.workflow_base_path / Path(f"{uuid4().hex[:6]}.ext")
            file_path.write_text(data=json.dumps(input_dataset_dict))
            task.tag(path=file_path, tags=Tag.input_dataset())
            input_dataset_object = json.loads(json.dumps(input_dataset_dict))
            yield task, input_dataset_object
            task.scratch.purge()
            task.constants._purge()

    return construct_task


class FakeGQLClient:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def execute_gql_query(**kwargs):
        query_base = kwargs["query_base"]

        if query_base == "recipeRuns":
            return [
                RecipeRunResponse(
                    recipeInstanceId=1,
                    recipeInstance=RecipeInstanceResponse(
                        recipeId=1,
                        inputDataset=InputDatasetResponse(
                            inputDatasetId=1,
                            isActive=True,
                            inputDatasetDocument='{"bucket": "bucket-name", "parameters": [{"parameterName": "", "parameterValues": [{"parameterValueId": 1, "parameterValue": "[[1,2,3],[4,5,6],[7,8,9]]", "parameterValueStartDate": "1/1/2000"}]}], "frames": ["objectKey1", "objectKey2", "objectKeyN"]}',
                        ),
                    ),
                    configuration=f'{{"tile_size": {TILE_SIZE}}}',
                ),
            ]

    @staticmethod
    def execute_gql_mutation(**kwargs):
        ...


class FakeGQLClientNoRecipeConfiguration:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def execute_gql_query(**kwargs):
        query_base = kwargs["query_base"]

        if query_base == "recipeRuns":
            return [
                RecipeRunResponse(
                    recipeInstanceId=1,
                    recipeInstance=RecipeInstanceResponse(
                        recipeId=1,
                        inputDataset=InputDatasetResponse(
                            inputDatasetId=1,
                            isActive=True,
                            inputDatasetDocument='{"bucket": "bucket-name", "parameters": [{"parameterName": "", "parameterValues": [{"parameterValueId": 1, "parameterValue": "[[1,2,3],[4,5,6],[7,8,9]]", "parameterValueStartDate": "1/1/2000"}]}], "frames": ["objectKey1", "objectKey2", "objectKeyN"]}',
                        ),
                    ),
                ),
            ]

    @staticmethod
    def execute_gql_mutation(**kwargs):
        ...


# All of the following stuff is copied from dkist-processing-pac
def compute_telgeom(time_hst: Time):
    dkist_lon = (156 + 15 / 60.0 + 21.7 / 3600.0) * (-1)
    dkist_lat = 20 + 42 / 60.0 + 27.0 / 3600.0
    hel = 3040.4
    hloc = coordinates.EarthLocation.from_geodetic(dkist_lon, dkist_lat, hel)
    sun_body = coordinates.get_body("sun", time_hst, hloc)  # get the solar ephemeris
    azel_frame = coordinates.AltAz(obstime=time_hst, location=hloc)  # Horizon coords
    sun_altaz = sun_body.transform_to(azel_frame)  # Sun in horizon coords
    alt = sun_altaz.alt.value  # Extract altitude
    azi = sun_altaz.az.value  # Extract azimuth

    tableang = alt - azi

    return {"TELEVATN": alt, "TAZIMUTH": azi, "TTBLANGL": tableang}


class CalibrationSequenceStepDataset(Spec122Dataset):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        time_delta: float,
        pol_status: str,
        pol_theta: float,
        ret_status: str,
        ret_theta: float,
        dark_status: str,
        instrument: str = "visp",
        num_mod: int = 3,
        start_time: Union[str, datetime] = None,
    ):
        self.num_mod = num_mod

        # Make up a Calibration sequence. Mostly random except for two clears and two darks at start and end, which
        # we want to test
        self.pol_status = pol_status
        self.pol_theta = pol_theta
        self.ret_status = ret_status
        self.ret_theta = ret_theta
        self.dark_status = dark_status
        dataset_shape = (self.num_mod,) + array_shape[1:]
        super().__init__(
            dataset_shape, array_shape, time_delta, instrument=instrument, start_time=start_time
        )
        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("WAVELNTH", 666.0)

    @key_function("VISP_011")
    def modstate(self, key: str) -> int:
        return (self.index % self.num_mod) + 1

    @key_function("VISP_010")
    def nummod(self, key: str) -> int:
        return self.num_mod

    @key_function("PAC__004")
    def polarizer_status(self, key: str) -> str:
        return self.pol_status

    @key_function("PAC__005")
    def polarizer_angle(self, key: str) -> str:
        return "none" if self.pol_status == "clear" else str(self.pol_theta)

    @key_function("PAC__006")
    def retarter_status(self, key: str) -> str:
        return self.ret_status

    @key_function("PAC__007")
    def retarder_angle(self, key: str) -> str:
        return "none" if self.ret_status == "clear" else str(self.ret_theta)

    @key_function("PAC__008")
    def gos_level3_status(self, key: str) -> str:
        return self.dark_status

    @key_function("TAZIMUTH", "TELEVATN", "TTBLANGL")
    def telescope_geometry(self, key: str):
        return compute_telgeom(Time(self.date_obs(key), format="fits"))[key]


class InstAccess(L0FitsAccess):
    def __init__(self, hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU]):
        super().__init__(hdu, auto_squeeze=False)
        self.modulator_state = self.header["VSPSTNUM"]
        self.number_of_modulator_states = self.header["VSPNUMST"]


@pytest.fixture(scope="session")
def cs_with_correct_geometry():
    dark_status = [
        "DarkShutter",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "FieldStop (5arcmin)",
        "DarkShutter",
    ]
    ret_theta = [0, 0, 0, 0, 0, 0, 60, 120, 30, 90, 150, 0, 0, 0]
    ret_status = [
        "clear",
        "clear",
        "clear",
        "clear",
        "clear",
        "SiO2 SAR",
        "SiO2 SAR",
        "SiO2 SAR",
        "SiO2 SAR",
        "SiO2 SAR",
        "SiO2 SAR",
        "SiO2 SAR",
        "clear",
        "clear",
    ]
    pol_theta = [0, 0, 0, 60, 120, 0, 0, 0, 45, 45, 45, 45, 0, 0]
    pol_status = [
        "clear",
        "clear",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "Sapphire Polarizer",
        "clear",
        "clear",
    ]
    data_shape = (1, 1, 1)
    num_steps = len(pol_theta)
    out_dict = dict()
    start_time = datetime.fromisoformat("2022-05-25T12:00:00")
    for n in range(num_steps):
        ds = CalibrationSequenceStepDataset(
            array_shape=(1, 2, 2),
            time_delta=2.0,
            pol_status=pol_status[n],
            pol_theta=pol_theta[n],
            ret_status=ret_status[n],
            ret_theta=ret_theta[n],
            dark_status=dark_status[n],
            start_time=start_time,
            num_mod=10,
        )
        header_list = [
            spec122_validator.validate_and_translate_to_214_l0(
                d.header(), return_type=fits.HDUList
            )[0].header
            for d in ds
        ]
        hdu_list = []
        for m in range(ds.num_mod):
            hdu_list.append(
                fits.PrimaryHDU(
                    data=np.ones(data_shape) * 1e3, header=fits.Header(header_list.pop(0))
                )
            )

        out_dict[n] = [InstAccess(h) for h in hdu_list]
        start_time = ds.start_time + timedelta(seconds=60)

    return out_dict, data_shape


@pytest.fixture(scope="session")
def pac_fit_mode() -> str:
    return "use_M12"


@pytest.fixture(scope="session")
def pac_init_set() -> str:
    return "OCCal_VIS"


@pytest.fixture(scope="session")
def visp_modulation_matrix() -> np.ndarray:
    # Modulation matrix for AdW's synthetic ViSP data from mod_matrix_630.out
    return np.array(
        [
            [1.0, 0.19155013, 0.80446989, -0.47479524],
            [1.0, -0.65839661, 0.68433984, 0.00466389],
            [1.0, -0.80679413, -0.16112977, 0.48234158],
            [1.0, -0.04856211, -0.56352868, 0.77578117],
            [1.0, 0.56844858, 0.03324473, 0.77289873],
            [1.0, 0.19155013, 0.80446989, 0.47479524],
            [1.0, -0.65839661, 0.68433984, -0.00466389],
            [1.0, -0.80679413, -0.16112977, -0.48234158],
            [1.0, -0.04856211, -0.56352868, -0.77578117],
            [1.0, 0.56844858, 0.03324473, -0.77289873],
        ],
        dtype=np.float64,
    )


@pytest.fixture(scope="session")
def fully_realistic_cs(
    cs_with_correct_geometry, visp_modulation_matrix, pac_fit_mode, pac_init_set
):

    cs_dict, data_shape = cs_with_correct_geometry
    dresser = Dresser()
    dresser.add_drawer(Drawer(cs_dict, skip_darks=False))
    CM = CalibrationUnit(dresser)
    TM = Telescope(dresser)
    full_params = PolcalDresserParameters(dresser, pac_fit_mode, pac_init_set)

    global_params = full_params.init_params._all_parameters[0]
    pardict = global_params.valuesdict()
    CM.load_pars_from_dict(pardict)
    TM.load_pars_from_dict(pardict)

    CM.I_sys[0] = 1e4

    # Has shape (4, N)
    S = np.sum((TM.TM @ CM.CM @ TM.M12) * CM.S_in[:, None, :], axis=2).T

    # Has shape (M, N)
    observed = visp_modulation_matrix @ S

    # Now set the "observed" value for each of the input objects
    for m in range(dresser.nummod):
        for n in range(dresser.numsteps):
            cs_dict[n][m].data *= observed[m, n] / np.mean(cs_dict[n][m].data)

    return cs_dict


@pytest.fixture(scope="session")
def fully_realistic_dresser(fully_realistic_cs):
    dresser = Dresser()
    dresser.add_drawer(Drawer(fully_realistic_cs))
    return dresser


@pytest.fixture(scope="session")
def initialized_polcal_fitter(fully_realistic_dresser, pac_init_set, pac_fit_mode) -> PolcalFitter:
    return PolcalFitter(
        local_dresser=fully_realistic_dresser,
        global_dresser=fully_realistic_dresser,
        fit_mode=pac_fit_mode,
        init_set=pac_init_set,
        fit_TM=False,
    )
