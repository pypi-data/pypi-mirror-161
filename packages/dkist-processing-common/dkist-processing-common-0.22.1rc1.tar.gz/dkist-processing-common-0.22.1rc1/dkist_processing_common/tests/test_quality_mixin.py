import datetime
import json

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.json_encoder import QualityValueEncoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.quality import QualityMixin


class Task(WorkflowTaskBase, QualityMixin):
    def run(self):
        pass


@pytest.fixture
def quality_task(tmp_path, recipe_run_id):
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        yield task
        task.scratch.purge()
        task.constants._purge()


@pytest.fixture
def plot_data():
    datetimes_a = ["2021-01-01T01:01:01", "2021-01-01T02:01:01"]
    values_a = [3, 4]
    datetimes_b = ["2020-01-01T01:01:01", "2020-01-01T02:01:01"]
    values_b = [1, 2]
    return datetimes_a, values_a, datetimes_b, values_b


def test_format_warnings(quality_task):
    """
    Given: a task with the QualityMixin
    When: checking the format of warnings
    Then: an empty list of warnings is converted to None
    """
    task = quality_task
    warnings = task._format_warnings(warnings=[])
    assert warnings is None


def test_create_2d_plot_with_datetime_metric(quality_task):
    """
    Given: a task with the QualityMixin
    When: submitting data to create a 2d plot metric
    Then: the metric is encoded with the expected schema
    """
    task = quality_task
    name = "test_metric"
    description = "test_description"
    xlabel = "xlabel"
    ylabel = "ylabel"
    xdata = ["2020-01-01T01:01:01", "2020-01-01T02:01:01"]
    ydata = [1, 2]
    series_data = {"": [xdata, ydata]}
    statement = "test_statement"
    warnings = ["WARNING A", "WARNING B"]
    json_metric: dict = task._create_2d_plot_with_datetime_metric(
        name=name,
        description=description,
        xlabel=xlabel,
        ylabel=ylabel,
        series_data=series_data,
        statement=statement,
        warnings=warnings,
    )
    assert list(json_metric.keys()) == [
        "name",
        "description",
        "statement",
        "plot_data",
        "histogram_data",
        "table_data",
        "modmat_data",
        "efficiency_data",
        "raincloud_data",
        "warnings",
    ]
    assert json_metric["name"] == name
    assert json_metric["description"] == description
    assert json_metric["statement"] == statement
    assert json_metric["warnings"] == warnings
    assert json_metric["table_data"] is None
    assert json_metric["plot_data"]["series_data"][""][0] == [
        datetime.datetime.fromisoformat(i) for i in xdata
    ]
    assert json_metric["plot_data"]["series_data"][""][1] == ydata


def test_record_2d_plot_values(quality_task):
    """
    Given: a task with the QualityMixin
    When: recording 2d plot data to disk
    Then: the metric is recorded with the expected schema
    """
    task = quality_task
    xdata = ["2020-01-01T01:01:01", "2020-01-01T02:01:01"]
    ydata = [1, 2]
    tag = Tag.quality("2D_PLOT")
    task._record_2d_plot_values(x_values=xdata, y_values=ydata, tags=tag)
    task._record_2d_plot_values(x_values=xdata, y_values=ydata, tags=tag)
    files = list(task.read(tags=Tag.quality("2D_PLOT")))
    assert len(files) == 2
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert data["x_values"] == xdata
            assert data["y_values"] == ydata


def test_load_2d_plot_values(quality_task, plot_data):
    """
    Given: a task with the QualityMixin and multiple 2d plot data files on disk
    When: loading the 2d plot data
    Then: data is returned merged
    """
    task = quality_task
    tag = Tag.quality("MERGED")
    datetimes_a, values_a, datetimes_b, values_b = plot_data
    task._record_2d_plot_values(x_values=datetimes_a, y_values=values_a, tags=tag)
    task._record_2d_plot_values(x_values=datetimes_b, y_values=values_b, tags=tag)
    datetimes, values = list(task._load_2d_plot_values(tags=tag).values())[0]
    assert len(datetimes) == len(datetimes_a) + len(datetimes_b)
    for i in datetimes:
        assert i in datetimes_a + datetimes_b
    assert len(values) == len(values_a) + len(values_b)
    for i in values:
        assert i in values_a + values_b


def test_find_iqr_outliers(quality_task):
    """
    Given: a task with the QualityMixin
    When: checking data for outliers
    Then: the correct outliers are found
    """
    task = quality_task
    datetimes = ["a", "b", "c", "d", "e"]
    values = [5.1, 4.9, 9.3, 5.3, 4.9]
    warnings = task._find_iqr_outliers(datetimes=datetimes, values=values)
    assert warnings == [
        "File with datetime c has a value considered to be an outlier " "for this metric"
    ]


def test_fried_parameter(quality_task):
    """
    Given: a task with the QualityMixin
    When: writing fried parameter data
    Then: the data written matches what was given
    """
    task = quality_task
    datetimes = ["2020-01-01T01:01:01", "2020-01-01T02:01:01"]
    values = [1, 2]
    task.quality_store_fried_parameter(datetimes=datetimes, values=values)
    path = list(task.read(tags=Tag.quality("FRIED_PARAMETER")))
    assert len(path) == 1
    with path[0].open() as f:
        data = json.load(f)
        assert data["x_values"] == datetimes
        assert data["y_values"] == values


def test_build_fried_parameter(quality_task, plot_data):
    """
    Given: a task with the QualityMixin
    When: writing multiple fried parameter data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    datetimes_a, values_a, datetimes_b, values_b = plot_data
    task.quality_store_fried_parameter(datetimes=datetimes_a, values=values_a)
    task.quality_store_fried_parameter(datetimes=datetimes_b, values=values_b)
    path = list(task.read(tags=Tag.quality("FRIED_PARAMETER")))
    assert len(path) == 2
    metric = task.quality_build_fried_parameter()
    assert metric["plot_data"]["series_data"][""][0] == [
        datetime.datetime.fromisoformat(i)
        for i in [
            "2020-01-01T01:01:01",
            "2020-01-01T02:01:01",
            "2021-01-01T01:01:01",
            "2021-01-01T02:01:01",
        ]
    ]
    assert metric["plot_data"]["series_data"][""][1] == [1, 2, 3, 4]
    assert metric["name"] == "Fried Parameter"
    assert metric["warnings"] is None
    assert metric["statement"] == "Average Fried Parameter for L1 dataset: 2.5 ± 1.12 m"


def test_build_light_level(quality_task, plot_data):
    """
    Given: a task with the QualityMixin
    When: writing multiple light level data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    datetimes_a, values_a, datetimes_b, values_b = plot_data
    task.quality_store_light_level(datetimes=datetimes_a, values=values_a)
    task.quality_store_light_level(datetimes=datetimes_b, values=values_b)
    path = list(task.read(tags=Tag.quality("LIGHT_LEVEL")))
    assert len(path) == 2
    metric = task.quality_build_light_level()
    assert metric["plot_data"]["series_data"][""][0] == [
        datetime.datetime.fromisoformat(i)
        for i in [
            "2020-01-01T01:01:01",
            "2020-01-01T02:01:01",
            "2021-01-01T01:01:01",
            "2021-01-01T02:01:01",
        ]
    ]
    assert metric["plot_data"]["series_data"][""][1] == [1, 2, 3, 4]
    assert metric["name"] == "Light Level"
    assert metric["warnings"] is None
    assert metric["statement"] == f"Average Light Level for L1 dataset: 2.5 ± 1.12 adu"


def test_build_frame_average(quality_task, plot_data):
    """
    Given: a task with the QualityMixin
    When: writing multiple frame average data elements
    Then: a schema is built containing all elements and an appropriate warning is returned
    """
    task = quality_task
    datetimes_a, _, datetimes_b, _ = plot_data
    values_a = [5.1, 9.6]
    values_b = [5.2, 4.9]
    task.quality_store_frame_average(
        datetimes=datetimes_a, values=values_a, task_type="dark", modstate=1
    )
    task.quality_store_frame_average(
        datetimes=datetimes_b, values=values_b, task_type="dark", modstate=1
    )
    task.quality_store_frame_average(
        datetimes=datetimes_a, values=values_a, task_type="dark", modstate=2
    )
    task.quality_store_frame_average(
        datetimes=datetimes_b, values=values_b, task_type="dark", modstate=2
    )
    path = list(task.read(tags=[Tag.quality("FRAME_AVERAGE"), Tag.quality_task("dark")]))
    assert len(path) == 4
    metric = task.quality_build_frame_average(task_type="dark")
    for i in range(1, 3):
        assert metric["plot_data"]["series_data"][f"{i}"][0] == [
            datetime.datetime.fromisoformat(i)
            for i in [
                "2020-01-01T01:01:01",
                "2020-01-01T02:01:01",
                "2021-01-01T01:01:01",
                "2021-01-01T02:01:01",
            ]
        ]
    assert metric["name"] == "Average Across Frame - DARK"
    assert metric["warnings"] == [
        "File with datetime 2021-01-01T02:01:01 has a value considered "
        "to be an outlier for this metric"
    ]


def test_build_frame_rms(quality_task, plot_data):
    """
    Given: a task with the QualityMixin
    When: writing multiple frame rms data elements
    Then: a schema is built containing all elements and an appropriate warning is returned
    """
    task = quality_task
    datetimes_a, _, datetimes_b, _ = plot_data
    values_a = [5.1, 9.6]
    values_b = [5.2, 4.9]
    task.quality_store_frame_rms(
        datetimes=datetimes_a, values=values_a, task_type="gain", modstate=1
    )
    task.quality_store_frame_rms(
        datetimes=datetimes_a, values=values_a, task_type="gain", modstate=2
    )
    task.quality_store_frame_rms(
        datetimes=datetimes_b, values=values_b, task_type="gain", modstate=1
    )
    task.quality_store_frame_rms(
        datetimes=datetimes_b, values=values_b, task_type="gain", modstate=2
    )
    path = list(task.read(tags=Tag.quality("FRAME_RMS")))
    assert len(path) == 4
    metric = task.quality_build_frame_rms(task_type="gain")
    for i in range(1, 3):
        assert metric["plot_data"]["series_data"][f"{i}"][0] == [
            datetime.datetime.fromisoformat(i)
            for i in [
                "2020-01-01T01:01:01",
                "2020-01-01T02:01:01",
                "2021-01-01T01:01:01",
                "2021-01-01T02:01:01",
            ]
        ]
    assert metric["name"] == "Root Mean Square (RMS) Across Frame - GAIN"
    assert metric["warnings"] == [
        "File with datetime 2021-01-01T02:01:01 has a value considered "
        "to be an outlier for this metric"
    ]


def test_build_noise(quality_task, plot_data):
    """
    Given: a task with the QualityMixin
    When: writing multiple noise data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    datetimes_a, values_a, datetimes_b, values_b = plot_data
    for stokes in ["I", "Q", "U", "V"]:
        task.quality_store_noise(datetimes=datetimes_a, values=values_a, stokes=stokes)
        task.quality_store_noise(datetimes=datetimes_b, values=values_b, stokes=stokes)
        path = list(task.read(tags=[Tag.quality("NOISE"), Tag.stokes(stokes)]))
        assert len(path) == 2

    metric = task.quality_build_noise()
    assert sorted(list(metric["plot_data"]["series_data"].keys())) == sorted(["I", "Q", "U", "V"])
    assert metric["plot_data"]["series_data"]["I"][0] == [
        datetime.datetime.fromisoformat(i)
        for i in [
            "2020-01-01T01:01:01",
            "2020-01-01T02:01:01",
            "2021-01-01T01:01:01",
            "2021-01-01T02:01:01",
        ]
    ]
    assert metric["plot_data"]["series_data"]["I"][1] == [1, 2, 3, 4]
    assert metric["name"] == "Noise Estimation"
    assert metric["warnings"] is None


def test_build_sensitivity(quality_task, plot_data):
    """
    Given: a task with the QualityMixin
    When: writing multiple polarimetric noise data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    datetimes_a, values_a, datetimes_b, values_b = plot_data
    for stokes in ["I", "Q", "U", "V"]:
        task.quality_store_sensitivity(datetimes=datetimes_a, values=values_a, stokes=stokes)
        task.quality_store_sensitivity(datetimes=datetimes_b, values=values_b, stokes=stokes)
        path = list(task.read(tags=[Tag.quality("SENSITIVITY"), Tag.stokes(stokes)]))
        assert len(path) == 2

    metric = task.quality_build_sensitivity()
    assert sorted(list(metric["plot_data"]["series_data"].keys())) == sorted(["I", "Q", "U", "V"])
    assert metric["plot_data"]["series_data"]["I"][0] == [
        datetime.datetime.fromisoformat(i)
        for i in [
            "2020-01-01T01:01:01",
            "2020-01-01T02:01:01",
            "2021-01-01T01:01:01",
            "2021-01-01T02:01:01",
        ]
    ]
    assert metric["plot_data"]["series_data"]["I"][1] == [1, 2, 3, 4]
    assert metric["name"] == f"Sensitivity"
    assert metric["warnings"] is None


def test_create_table_metric(quality_task):
    """
    Given: a task with the QualityMixin
    When: submitting data to create a table metric
    Then: the metric is encoded with the expected schema
    """
    task = quality_task
    name = "table metric"
    description = "table metric description"
    rows = [["a", 1], ["b", 2], ["c", 3]]
    statement = "table statement"
    warnings = ["table warning"]
    table_metric = task._create_table_metric(
        name=name, description=description, rows=rows, statement=statement, warnings=warnings
    )
    assert table_metric["name"] == name
    assert table_metric["description"] == description
    assert table_metric["statement"] == statement
    assert table_metric["table_data"] == {"header_column": False, "header_row": True, "rows": rows}
    assert table_metric["warnings"] == warnings


def test_build_health_status(quality_task):
    """
    Given: a task with the QualityMixin
    When: writing multiple health status data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    task.quality_store_health_status(values=["Good", "Good", "Good"])
    task.quality_store_health_status(values=["Unknown", "Ill", "Bad"])
    path = list(task.read(tags=Tag.quality("HEALTH_STATUS")))
    assert len(path) == 2
    metric = task.quality_build_health_status()
    assert metric["name"] == "Data Source Health"
    assert metric["warnings"] == [
        "Data sourced from components with a health status of 'ill', 'bad', or 'unknown'."
    ]
    assert metric["table_data"]["rows"] == [
        ["Status", "Count"],
        ["bad", 1],
        ["good", 3],
        ["ill", 1],
        ["unknown", 1],
    ]


def test_build_task_type_counts(quality_task):
    """
    Given: a task with the QualityMixin
    When: writing multiple task type count data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    task.quality_store_task_type_counts(task_type="dark", total_frames=109, frames_not_used=0)
    task.quality_store_task_type_counts(task_type="gain", total_frames=276, frames_not_used=58)
    task.quality_store_task_type_counts(task_type="foo", total_frames=0, frames_not_used=0)
    path = list(task.read(tags=Tag.quality("TASK_TYPES")))
    assert len(path) == 3
    metric = task.quality_build_task_type_counts()
    assert metric["name"] == "Frame Counts"
    assert "21.0% of frames were not used in the processing of task type GAIN" in metric["warnings"]
    assert "NO FOO frames were used!" in metric["warnings"]


def test_build_dataset_average(quality_task):
    """
    Given: a task with the QualityMixin
    When: writing multiple dataset average data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    task.quality_store_dataset_average(task_type="dark", frame_averages=[1, 5, 3, 4, 6])
    task.quality_store_dataset_average(task_type="dark", frame_averages=[1, 9, 4, 7, 2])
    task.quality_store_dataset_average(task_type="gain", frame_averages=[5, 8, 3, 7, 8])
    path = list(task.read(tags=Tag.quality("DATASET_AVERAGE")))
    assert len(path) == 3
    metric = task.quality_build_dataset_average()
    assert metric["name"] == "Average Across Dataset"
    assert metric["warnings"] is None


def test_build_dataset_rms(quality_task):
    """
    Given: a task with the QualityMixin
    When: writing multiple dataset rms data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    task.quality_store_dataset_rms(task_type="dark", frame_rms=[1, 5, 3, 4, 6])
    task.quality_store_dataset_rms(task_type="dark", frame_rms=[1, 9, 4, 7, 2])
    task.quality_store_dataset_rms(task_type="gain", frame_rms=[5, 8, 3, 7, 8])
    path = list(task.read(tags=Tag.quality("DATASET_RMS")))
    assert len(path) == 3
    metric = task.quality_build_dataset_rms()
    assert metric["name"] == "Dataset RMS"
    assert metric["warnings"] is None


def test_build_historical(quality_task):
    """
    Given: a task with the QualityMixin
    When: writing multiple historical data elements
    Then: a schema is built containing all elements
    """
    task = quality_task
    task.quality_store_historical(name="metric 1", value=5, warning="warning for metric 1")
    task.quality_store_historical(name="metric 2", value="abc")
    task.quality_store_historical(name="metric 3", value=6.38)
    path = list(task.read(tags=Tag.quality("HISTORICAL")))
    assert len(path) == 3
    metric = task.quality_build_historical()
    assert metric["name"] == "Historical Comparisons"
    assert metric["warnings"] == ["warning for metric 1"]


def test_create_statement_metric(quality_task):
    """
    Given: a task with the QualityMixin
    When: submitting data to create a statement metric
    Then: the metric is encoded with the expected schema
    """
    task = quality_task
    name = "statement metric"
    description = "statement description"
    statement = "statement statement"
    warnings = ["statement warnings"]
    metric = task._create_statement_metric(
        name=name, description=description, statement=statement, warnings=warnings
    )
    assert metric["name"] == name
    assert metric["description"] == description
    assert metric["statement"] == statement
    assert metric["warnings"] == warnings


def test_build_ao_status(quality_task):
    """
    Given: a task with the QualityMixin
    When: submitting data to create the ao status metric metric
    Then: the metric is encoded with the expected schema
    """
    task = quality_task
    task.quality_store_ao_status(values=[1, 1, 1, 1, 1, 1, 1, 1])
    task.quality_store_ao_status(values=[0, 0, 1, 1, 1, 1, 1, 1])
    path = list(task.read(tags=Tag.quality("AO_STATUS")))
    assert len(path) == 2
    metric = task.quality_build_ao_status()
    assert metric["name"] == "Adaptive Optics Status"
    assert (
        metric["statement"] == "The adaptive optics system was running and locked for 87.5% "
        "of the observed frames"
    )


def test_build_range(quality_task):
    """
    Given: a task with the QualityMixin
    When: submitting data to create a number of range metrics
    Then: the metric is encoded with the expected schema
    """
    task = quality_task
    task.quality_store_range(name="range metric 1", warnings=["warning for range metric 1"])
    task.quality_store_range(
        name="range metric 2", warnings=["warning for range metric 2", "another warning"]
    )
    path = list(task.read(tags=Tag.quality("RANGE")))
    assert len(path) == 2
    metric = task.quality_build_range()
    assert metric["name"] == "Range checks"
    assert len(metric["warnings"]) == 3


def test_build_report(quality_task, plot_data):
    """
    Given: a task with the QualityMixin and data on disk for multiple metrics
    When: building the quality report
    Then: the report is encoded with the expected schema
    """
    task = quality_task
    datetimes, values, _, _ = plot_data
    task.quality_store_task_type_counts(task_type="dark", total_frames=100, frames_not_used=7)
    task.quality_store_task_type_counts(task_type="gain", total_frames=100, frames_not_used=0)
    task.quality_store_fried_parameter(datetimes=datetimes, values=values)
    task.quality_store_light_level(datetimes=datetimes, values=values)
    task.quality_store_frame_average(
        datetimes=datetimes, values=values, task_type="dark", modstate=1
    )
    task.quality_store_frame_average(
        datetimes=datetimes, values=values, task_type="dark", modstate=2
    )
    task.quality_store_frame_average(
        datetimes=datetimes, values=values, task_type="gain", modstate=1
    )
    task.quality_store_frame_average(
        datetimes=datetimes, values=values, task_type="gain", modstate=2
    )
    task.quality_store_frame_rms(datetimes=datetimes, values=values, task_type="dark")
    task.quality_store_frame_rms(datetimes=datetimes, values=values, task_type="gain")
    task.quality_store_dataset_average(task_type="dark", frame_averages=[1, 2, 3, 4, 5])
    task.quality_store_dataset_average(task_type="dark", frame_averages=[6, 7, 8, 9, 10])
    task.quality_store_dataset_average(task_type="gain", frame_averages=[6, 7, 8, 9, 10])
    task.quality_store_dataset_rms(task_type="dark", frame_rms=[1, 2, 3, 4, 5])
    task.quality_store_dataset_rms(task_type="dark", frame_rms=[6, 7, 8, 9, 10])
    task.quality_store_dataset_rms(task_type="gain", frame_rms=[6, 7, 8, 9, 10])
    task.quality_store_noise(datetimes=datetimes, values=values)
    task.quality_store_range(name="metric 1", warnings=["warning 1"])
    task.quality_store_range(name="metric 2", warnings=["warning 2"])
    task.quality_store_range(name="metric 3", warnings=["warning 3"])
    task.quality_store_health_status(values=["Good", "Good", "Good", "Good", "Good", "Ill"])
    task.quality_store_ao_status(values=[1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0])
    task.quality_store_sensitivity(datetimes=datetimes, values=values, stokes="I")
    task.quality_store_sensitivity(datetimes=datetimes, values=values, stokes="Q")
    task.quality_store_sensitivity(datetimes=datetimes, values=values, stokes="U")
    task.quality_store_sensitivity(datetimes=datetimes, values=values, stokes="V")
    task.quality_store_historical(name="hist 1", value=7)
    task.quality_store_historical(name="hist 2", value="abc")
    task.quality_store_historical(
        name="hist 3", value=9.35, warning="warning for historical metric 3"
    )

    report = task.quality_build_report()
    assert len(report) == 16
    assert report[-1]["name"] == "Warnings count"
    assert (
        report[-1]["statement"] == "6 warnings were raised during the calibration of this dataset"
    )


@pytest.fixture
def polcal_global_params_json():
    label = "Beam 1"
    data = {
        "task_type": label,
        "bin_1_str": "2 spatial",
        "bin_2_str": "3 radical",
        "param_names": ["par1", "par2", "par3"],
        "param_vary": [True, True, False],
        "param_init_vals": [0.1, 0.2, 0.3],
        "param_fit_vals": [1, 2.222, 0.33],
        "param_diffs": [4, 1.1, 0.2],
        "param_ratios": [3, 2, "-"],
        "warnings": ["A thing is bad"],
    }

    return json.dumps(data, allow_nan=False, cls=QualityValueEncoder).encode(), label


def test_polcal_build_global_parameter_values(quality_task, polcal_global_params_json):
    """
    Given: A task with the PolcalQualityMixin
    When: Building the global parameter QA metric
    Then: The correct dictionary is returned
    """
    data, label = polcal_global_params_json
    quality_task.write(data, tags=[Tag.quality("POLCAL_GLOBAL_PAR_VALS"), Tag.quality_task(label)])
    metric = quality_task.quality_build_polcal_global_parameter_values(label=label)

    assert metric["name"] == f"PolCal Global Calibration Unit Fit - {label}"
    assert metric["warnings"] == ["A thing is bad"]
    metric_table = metric["table_data"]["rows"]
    assert len(metric_table) == 4  # 3 rows + one for header
    assert metric_table[1] == ["par1", True, f"{0.1: 6.2f}", f"{1: 6.2f}", f"{4: .2e}", f"{3: .2e}"]
    assert metric_table[2] == [
        "par2",
        True,
        f"{0.2: 6.2f}",
        f"{2.222: 6.2f}",
        f"{1.1: .2e}",
        f"{2: .2e}",
    ]
    assert metric_table[3] == ["par3", False, f"{0.3: 6.2f}", f"{0.33: 6.2f}", f"{0.2: .2e}", "-"]


@pytest.fixture
def polcal_local_params_json():
    label = "Beam 1"
    data = {
        "task_type": label,
        "bin_1_str": "2 spatial",
        "bin_2_str": "3 radical",
        "total_bins": 6,
        "modmat_list": [[[1, 2.0], [2.0, 3.0]], [[10.0, 20.0], [20.0, 30.0]]],
        "I_sys_list": [1, 2, 3],
        "I_sys_init": 6.28,
    }

    return json.dumps(data, allow_nan=False, cls=QualityValueEncoder).encode(), label


def test_polcal_build_local_parameter_values(quality_task, polcal_local_params_json):
    """
    Given: A task with the PolcalQualityMixin
    When: Building the local parameter QA metric
    Then: The correct dictionary is returned
    """
    data, label = polcal_local_params_json
    quality_task.write(data, tags=[Tag.quality("POLCAL_LOCAL_PAR_VALS"), Tag.quality_task(label)])
    metric = quality_task.quality_build_polcal_local_parameter_values(label=label)

    assert metric["name"] == f"PolCal Local Bin Fits - {label}"
    modmat_data = metric["modmat_data"]
    assert modmat_data["modmat_list"] == [[[1, 2.0], [2.0, 3.0]], [[10.0, 20.0], [20.0, 30.0]]]
    I_sys_data = metric["histogram_data"]
    assert I_sys_data["xlabel"] == "I_sys"
    assert I_sys_data["series_data"] == {"I_sys": [1, 2, 3]}
    assert I_sys_data["vertical_lines"] == {"I_clear": 6.28}


@pytest.fixture
def polcal_fit_residuals_json():
    label = "Beam 1"
    data = {
        "task_type": label,
        "bin_1_str": "2 spatial",
        "bin_2_str": "3 radical",
        "total_bins": 6,
        "residual_json": json.dumps("Just some garbage"),
        "red_chi_list": [1.0, 2.0, 3.0],
    }

    return json.dumps(data, allow_nan=False, cls=QualityValueEncoder).encode(), label


def test_polcal_build_fit_residuals(quality_task, polcal_fit_residuals_json):
    """
    Given: A task with the PolcalQualityMixin
    When: Building the fit residual QA metric
    Then: The correct dictionary is returned
    """
    data, label = polcal_fit_residuals_json
    quality_task.write(data, tags=[Tag.quality("POLCAL_FIT_RESIDUALS"), Tag.quality_task(label)])
    metric = quality_task.quality_build_polcal_fit_residuals(label=label)

    assert metric["name"] == f"PolCal Fit Residuals - {label}"

    chisq_data = metric["histogram_data"]
    assert chisq_data["xlabel"] == "Reduced Chisq"
    assert chisq_data["series_data"] == {"Red chisq": [1.0, 2.0, 3.0]}
    assert chisq_data["vertical_lines"] == {"Mean = 2.00": 2.0}

    violin_data = metric["raincloud_data"]
    assert violin_data["xlabel"] == "CS Step"
    assert violin_data["ylabel"] == r"$\frac{I_{fit} - I_{obs}}{\sigma_I}$"
    assert violin_data["dataframe_json"] == json.dumps("Just some garbage")


@pytest.fixture
def polcal_efficiency_json():
    label = "Beam 1"
    data = {
        "task_type": label,
        "bin_1_str": "2 spatial",
        "bin_2_str": "3 radical",
        "total_bins": 6,
        "efficiency_list": [[1.0, 2.0], [2.0, 3.0]],
        "warnings": [],
    }

    return json.dumps(data, allow_nan=False, cls=QualityValueEncoder).encode(), label


def test_polcal_build_efficiency(quality_task, polcal_efficiency_json):
    """
    Given: A task with the PolcalQualityMixin
    When: Building the modulation efficiency QA metric
    Then: The correct dictionary is returned
    """
    data, label = polcal_efficiency_json
    quality_task.write(data, tags=[Tag.quality("POLCAL_EFFICIENCY"), Tag.quality_task(label)])
    metric = quality_task.quality_build_polcal_efficiency(label=label)

    assert metric["name"] == f"PolCal Modulation Efficiency - {label}"
    efficiency_data = metric["efficiency_data"]
    assert efficiency_data["efficiency_list"] == [[1.0, 2.0], [2.0, 3.0]]
