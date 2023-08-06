"""Collection of Mixin classes supporting different types of quality metrics.

These classes should not be directly mixed in to anything. They are pre-mixed into the top-level QualityMixin
"""
import copy
import json
import logging
from collections import defaultdict
from datetime import datetime
from functools import partial
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import numpy as np
from dkist_processing_pac.fitter.fitter_parameters import CU_PARAMS
from dkist_processing_pac.fitter.fitter_parameters import GLOBAL_PARAMS
from dkist_processing_pac.fitter.fitting_core import compare_I
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from pandas import DataFrame

from dkist_processing_common.models.quality import EfficiencyHistograms
from dkist_processing_common.models.quality import ModulationMatrixHistograms
from dkist_processing_common.models.quality import Plot2D
from dkist_processing_common.models.quality import PlotHistogram
from dkist_processing_common.models.quality import PlotRaincloud
from dkist_processing_common.models.quality import ReportMetric
from dkist_processing_common.models.quality import SimpleTable
from dkist_processing_common.models.tags import Tag


class _SimpleQualityMixin:
    @staticmethod
    def _create_statement_metric(
        name: str, description: str, statement: str, warnings: Optional[str] = None
    ) -> dict:
        metric = ReportMetric(
            name=name, description=description, statement=statement, warnings=warnings
        )
        return metric.dict()

    def quality_store_ao_status(self, values: List[bool]):
        """
        Collect and store ao status data.

        Parameters
        ----------
        values: boolean value denoting whether AO was running and locked or not
        """
        self._record_values(values=values, tags=Tag.quality("AO_STATUS"))

    def quality_build_ao_status(self) -> dict:
        """Build ao status schema from stored data."""
        ao_status = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("AO_STATUS")):
            with path.open() as f:
                ao_status += json.load(f)
        percentage = round(100 * np.count_nonzero(ao_status) / len(ao_status), 1)
        return self._create_statement_metric(
            name="Adaptive Optics Status",
            description="This metric shows the percentage of frames in which the adaptive optics "
            "system was running and locked",
            statement=f"The adaptive optics system was running and locked for {percentage}% of the "
            f"observed frames",
            warnings=None,
        )

    def quality_store_range(self, name: str, warnings: List[str]):
        """
        Insert range checking warnings into the schema used to record quality info.

        Parameters
        ----------
        name: name of the parameter / measurement for which range was out of bounds
        warnings: list of warnings to be entered into the quality report
        """
        data = {"name": name, "warnings": warnings}
        self._record_values(values=data, tags=Tag.quality("RANGE"))

    def quality_build_range(self) -> dict:
        """Build range data schema from stored data."""
        warnings = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("RANGE")):
            with path.open() as f:
                data = json.load(f)
                for warning in data["warnings"]:
                    warnings.append(warning)

        return ReportMetric(
            name="Range checks",
            description="This metric is checking that certain input and calculated parameters "
            "fall within a valid data range. If no parameters are listed here, all "
            "pipeline parameters were measured to be in range",
            warnings=self._format_warnings(warnings),
        ).dict()


class _SimplePlotQualityMixin:
    """Mixin containing metrics that present as simple x/y plots."""

    @staticmethod
    def _create_2d_plot_with_datetime_metric(
        name: str,
        description: str,
        xlabel: str,
        ylabel: str,
        series_data: Dict[str, List[List[Any]]],
        series_name: Optional[str] = None,
        ylabel_horizontal: Optional[bool] = False,
        statement: Optional[str] = None,
        warnings: Optional[List[str]] = None,
    ) -> dict:
        for k, v in series_data.items():
            # Convert datetime strings to datetime objects
            series_data[k][0] = [datetime.fromisoformat(i) for i in v[0]]
            # Sort the lists to make sure they are in ascending time order
            series_data[k][0], series_data[k][1] = (list(t) for t in zip(*sorted(zip(v[0], v[1]))))
        plot_data = Plot2D(
            series_data=series_data,
            xlabel=xlabel,
            ylabel=ylabel,
            series_name=series_name,
            ylabel_horizontal=ylabel_horizontal,
        )
        metric = ReportMetric(
            name=name,
            description=description,
            statement=statement,
            plot_data=plot_data,
            warnings=warnings,
        )
        return metric.dict()

    def _record_2d_plot_values(
        self,
        x_values: Union[List[str]],
        y_values: List[float],
        tags: Union[Iterable[str], str],
        series_name: Optional[str] = "",
        task_type: Optional[str] = None,
    ):
        """
        Encode values for a 2d plot type metric and store as a file.

        Parameters
        ----------
        x_values: values to apply to the x axis of a 2d plot
        y_values: values to apply to the y axis of a 2d plot
        tags: list of tags relating to the specific quality parameter being stored
        series_name: name of the series if this is part of a multi series plot metric
        task_type: type of data to be used - dark, gain, etc
        """
        if isinstance(tags, str):
            tags = [tags]
        axis_are_different_lengths = len(x_values) != len(y_values)
        axis_are_zero_length = not x_values or not y_values
        if axis_are_different_lengths or axis_are_zero_length:
            raise ValueError(
                f"Cannot store 2D plot values with 0 length or different length axis. "
                f"{len(x_values)=}, {len(y_values)=}"
            )
        data = {"x_values": x_values, "y_values": y_values, "series_name": series_name}
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        self._record_values(values=data, tags=tags)

    def _load_2d_plot_values(self, tags: Union[str, List[str]], task_type: Optional[str] = None):
        """Load all quality files for a given tag and return the merged datetimes and values."""
        if isinstance(tags, str):
            tags = [tags]
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        all_plot_data = defaultdict(list)
        for path in self.read(tags=tags):
            with path.open() as f:
                data = json.load(f)
                series_name = data["series_name"]
                if series_name in all_plot_data.keys():
                    all_plot_data[series_name][0].extend(data["x_values"])
                    all_plot_data[series_name][1].extend(data["y_values"])
                else:
                    all_plot_data[series_name] = [data["x_values"], data["y_values"]]
        return all_plot_data

    @staticmethod
    def _find_iqr_outliers(datetimes: List[str], values: List[float]) -> List[str]:
        """
        Given a list of values, find values that fall more than (1.5 * iqr) outside the quartiles of the data.

        Parameters
        ----------
        datetimes: list of datetime strings used to reference the files that are outliers
        values: values to use to determine outliers from the iqr
        """
        if len(values) == 0:
            raise ValueError("No values provided.")
        warnings = []
        q1 = np.quantile(values, 0.25)
        q3 = np.quantile(values, 0.75)
        iqr = q3 - q1
        for i, val in enumerate(values):
            if val < q1 - (iqr * 1.5) or val > q3 + (iqr * 1.5):
                warnings.append(
                    f"File with datetime {datetimes[i]} has a value considered to be an outlier "
                    f"for this metric"
                )
        return warnings

    def quality_store_fried_parameter(self, datetimes: List[str], values: List[float]):
        """Collect and store datetime / value pairs for the fried parameter."""
        self._record_2d_plot_values(
            x_values=datetimes, y_values=values, tags=Tag.quality("FRIED_PARAMETER")
        )

    def quality_build_fried_parameter(self) -> dict:
        """Build fried parameter schema from stored data."""
        # Merge all recorded quality values
        series_data = self._load_2d_plot_values(tags=Tag.quality("FRIED_PARAMETER"))
        values = list(series_data.values())[0][1]
        return self._create_2d_plot_with_datetime_metric(
            name="Fried Parameter",
            description="This metric quantifies the stability of the atmosphere during an "
            "observation and directly impacts the data quality through a phenomenon "
            "known as atmospheric seeing. One measurement is taken per L1 frame.",
            xlabel="Time",
            ylabel="Fried Parameter (m)",
            series_data=series_data,
            statement=f"Average Fried Parameter for L1 dataset: "
            f"{round(np.mean(values), 2)} ± {round(np.std(values), 2)} m",
            warnings=None,
        )

    def quality_store_light_level(self, datetimes: List[str], values: List[float]):
        """Collect and store datetime / value pairs for the light level."""
        self._record_2d_plot_values(
            x_values=datetimes, y_values=values, tags=Tag.quality("LIGHT_LEVEL")
        )

    def quality_build_light_level(self) -> dict:
        """Build light_level schema from stored data."""
        series_data = self._load_2d_plot_values(tags=Tag.quality("LIGHT_LEVEL"))
        values = list(series_data.values())[0][1]
        return self._create_2d_plot_with_datetime_metric(
            name="Light Level",
            description="The telescope light level, as measured by the Telescope Acquisition Camera, at the start of "
            "data acquisition of each frame.",
            xlabel="Time",
            ylabel="Light Level (adu)",
            series_data=series_data,
            statement=f"Average Light Level for L1 dataset: "
            f"{round(np.mean(values), 2)} ± {round(np.std(values), 2)} adu",
            warnings=None,
        )

    def quality_store_frame_average(
        self,
        datetimes: List[str],
        values: List[float],
        task_type: str,
        modstate: Optional[int] = None,
    ):
        """Collect and store datetime / value pairs for the individual frame averages."""
        tags = [Tag.quality("FRAME_AVERAGE")]
        if modstate:
            tags.append(Tag.modstate(modstate))
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=tags,
            series_name=modstate or 1,
            task_type=task_type,
        )

    def quality_build_frame_average(
        self, task_type: str, num_modstates: Optional[int] = None
    ) -> dict:
        """Build frame average schema from stored data."""
        # No modstates
        series_data = self._load_2d_plot_values(
            tags=Tag.quality("FRAME_AVERAGE"), task_type=task_type
        )
        # With modstates
        if num_modstates:
            series_data = {}
            for m in range(1, num_modstates + 1):
                series_data.update(
                    self._load_2d_plot_values(
                        tags=[Tag.quality("FRAME_AVERAGE"), Tag.modstate(m)], task_type=task_type
                    )
                )
        # Build metric dict
        if len(series_data) > 0:
            datetimes, values = list(series_data.values())[0]
            warnings = self._find_iqr_outliers(datetimes=datetimes, values=values)
            return self._create_2d_plot_with_datetime_metric(
                name=f"Average Across Frame - {task_type.upper()}",
                description=f"Average intensity value across frames of task type {task_type}. One measurement is taken per frame in each task type.",
                xlabel="Time",
                ylabel="Average Value (adu / sec)",
                series_data=series_data,
                series_name="Modstate",
                warnings=self._format_warnings(warnings),
            )

    def quality_store_frame_rms(
        self,
        datetimes: List[str],
        values: List[float],
        task_type: str,
        modstate: Optional[int] = None,
    ):
        """Collect and store datetime / value pairs for the individual frame rms."""
        tags = [Tag.quality("FRAME_RMS")]
        if modstate:
            tags.append(Tag.modstate(modstate))
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=tags,
            series_name=modstate or 1,
            task_type=task_type,
        )

    def quality_build_frame_rms(self, task_type: str, num_modstates: Optional[int] = None) -> dict:
        """Build frame rms schema from stored data."""
        # No modstates
        series_data = self._load_2d_plot_values(tags=Tag.quality("FRAME_RMS"), task_type=task_type)
        # With modstates
        if num_modstates:
            series_data = {}
            for m in range(1, num_modstates + 1):
                series_data.update(
                    self._load_2d_plot_values(
                        tags=[Tag.quality("FRAME_RMS"), Tag.modstate(m)], task_type=task_type
                    )
                )
        # Build metric dict
        if len(series_data) > 0:
            datetimes, values = list(series_data.values())[0]
            warnings = self._find_iqr_outliers(datetimes=datetimes, values=values)
            return self._create_2d_plot_with_datetime_metric(
                name=f"Root Mean Square (RMS) Across Frame - {task_type.upper()}",
                description=f"RMS value across frames of task type {task_type}. One measurement is taken per frame in each task type.",
                xlabel="Time",
                ylabel="RMS (adu / sec)",
                series_data=series_data,
                series_name="Modstate",
                warnings=self._format_warnings(warnings),
            )

    def quality_store_noise(
        self, datetimes: List[str], values: List[float], stokes: Optional[str] = "I"
    ):
        """Collect and store datetime / value pairs for the noise data."""
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            series_name=stokes,
            tags=[Tag.quality("NOISE"), Tag.stokes(stokes)],
        )

    def quality_build_noise(self) -> dict:
        """Build noise schema from stored data."""
        series_data = self._load_2d_plot_values(tags=[Tag.quality("NOISE")])
        return self._create_2d_plot_with_datetime_metric(
            name=f"Noise Estimation",
            description="Estimate of the noise in L1 frames. Noise is computed as the average of the stddev of "
            "boxes/cubes that extend 1/5 from the edge of the images on all sides. "
            "One measurement taken per L1 frame.",
            xlabel="Time",
            ylabel="Noise (adu)",
            series_data=series_data,
            warnings=None,
        )

    def quality_store_sensitivity(
        self, stokes: Literal["I", "Q", "U", "V"], datetimes: List[str], values: List[float]
    ):
        """Collect and store datetime / value pairs for the polarimetric noise data."""
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            series_name=stokes,
            tags=[Tag.quality("SENSITIVITY"), Tag.stokes(stokes)],
        )

    def quality_build_sensitivity(self) -> dict:
        """Build polarimetric noise schema from stored data."""
        series_data = self._load_2d_plot_values(tags=[Tag.quality("SENSITIVITY")])
        return self._create_2d_plot_with_datetime_metric(
            name=f"Sensitivity",
            description=f"Sensitivity is defined as the stddev of a particular Stokes parameter divided by the signal in "
            f"Stokes I (computed as a median over the whole frame). One measurement is shown per map scan.",
            xlabel="Time",
            ylabel=r"$\frac{\sigma_X}{\mathrm{med}(I)}$",
            ylabel_horizontal=True,
            series_data=series_data,
            series_name="Stokes Parameter",
            warnings=None,
        )


class _TableQualityMixin:
    """Mixing for metrics that present as tables."""

    @staticmethod
    def _create_table_metric(
        name: str,
        description: str,
        rows: List[List[Any]],
        statement: Optional[str] = None,
        warnings: Optional[str] = None,
    ) -> dict:
        metric = ReportMetric(
            name=name,
            description=description,
            statement=statement,
            table_data=SimpleTable(rows=rows),
            warnings=warnings,
        )
        return metric.dict()

    def quality_store_health_status(self, values: List[str]):
        """
        Collect and store health status data.

        Parameters
        ----------
        values: statuses as listed in the headers
        """
        self._record_values(values=values, tags=Tag.quality("HEALTH_STATUS"))

    def quality_build_health_status(self) -> dict:
        """Build health status schema from stored data."""
        values = []
        for path in self.read(tags=Tag.quality("HEALTH_STATUS")):
            with path.open() as f:
                data = json.load(f)
                values += data
        statuses, counts = np.unique(values, return_counts=True)
        statuses = [s.lower() for s in statuses]
        # JSON serialization does not work with numpy types
        counts = [int(c) for c in counts]
        warnings = []
        if any(s in statuses for s in ["bad", "ill", "unknown"]):
            warnings.append(
                "Data sourced from components with a health status of 'ill', 'bad', or 'unknown'."
            )
        table_data = [list(z) for z in zip(statuses, counts)]
        table_data.insert(0, ["Status", "Count"])
        return self._create_table_metric(
            name="Data Source Health",
            description="This metric contains the worst health status of the data source during "
            "data acquisition. One reading is taken per L1 frame.",
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_task_type_counts(
        self, task_type: str, total_frames: int, frames_not_used: Optional[int] = 0
    ):
        """
        Collect and store task type data.

        Parameters
        ----------
        task_type: task type as listed in the headers
        total_frames: total number of frames supplied of the given task type
        frames_not_used: if some frames aren't used, how many
        """
        data = {
            "task_type": task_type.upper(),
            "total_frames": total_frames,
            "frames_not_used": frames_not_used,
        }
        self._record_values(values=data, tags=Tag.quality("TASK_TYPES"))

    def quality_build_task_type_counts(self) -> dict:
        """Build task type count schema from stored data."""
        # Raise warning if more than 5% of frames of a given type are not used
        warning_count_threshold = 0.05
        default_int_dict = partial(defaultdict, int)
        task_type_counts = defaultdict(default_int_dict)
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("TASK_TYPES")):
            with path.open() as f:
                data = json.load(f)
                task_type_counts[data["task_type"]]["total_frames"] += data["total_frames"]
                task_type_counts[data["task_type"]]["frames_not_used"] += data["frames_not_used"]

        # Now, build metric from the counts dict
        table_data = [[i[0]] + list(i[1].values()) for i in task_type_counts.items()]
        warnings = []
        for row in table_data:
            if row[1] == 0:
                warnings.append(f"NO {row[0]} frames were used!")
            elif row[2] / row[1] > warning_count_threshold:
                warnings.append(
                    f"{round(100 * row[2] / row[1], 1)}% of frames were not used in the "
                    f"processing of task type {row[0]}"
                )
        # Add header row
        table_data.insert(0, ["Task Type", "Total Frames", "Unused Frames"])
        return self._create_table_metric(
            name="Frame Counts",
            description="This metric is a count of the number of frames used to produce a "
            "calibrated L1 dataset",
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_dataset_average(self, task_type: str, frame_averages: List[float]):
        """
        Collect and store dataset average.

        Parameters
        ----------
        task_type: task type as listed in the headers
        frame_averages: average value of all pixels in each frame of the given task type
        """
        data = {"task_type": task_type, "frame_averages": frame_averages}
        self._record_values(values=data, tags=Tag.quality("DATASET_AVERAGE"))

    def quality_build_dataset_average(self) -> dict:
        """Build dataset average schema from stored data."""
        dataset_averages = defaultdict(list)
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("DATASET_AVERAGE")):
            with path.open() as f:
                data = json.load(f)
                # Add counts for the task type to its already existing counts
                dataset_averages[data["task_type"]] += data["frame_averages"]

        # Now, build metric from the counts dict
        table_data = [[i[0], round(np.mean(i[1]), 2)] for i in dataset_averages.items()]
        # Add header row
        table_data.insert(0, ["Task Type", "Dataset Average (adu / sec)"])
        return self._create_table_metric(
            name="Average Across Dataset",
            description="This metric is the calculated mean intensity value across data from an "
            "instrument program task type used in the creation of an entire L1 "
            "dataset.",
            rows=table_data,
            warnings=None,
        )

    def quality_store_dataset_rms(self, task_type: str, frame_rms: List[float]):
        """
        Collect and store dataset average.

        Parameters
        ----------
        task_type: task type as listed in the headers
        frame_rms: rms value of all pixels in each frame of the given task type
        """
        data = {"task_type": task_type, "frame_rms": frame_rms}
        self._record_values(values=data, tags=Tag.quality("DATASET_RMS"))

    def quality_build_dataset_rms(self) -> dict:
        """Build dataset rms schema from stored data."""
        dataset_rms = {}
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("DATASET_RMS")):
            with path.open() as f:
                data = json.load(f)
                # If the task type isn't in the dict, add it with counts set to zero
                if not data["task_type"] in dataset_rms.keys():
                    dataset_rms[data["task_type"]] = []
                # Add counts for the task type to its already existing counts
                dataset_rms[data["task_type"]] += data["frame_rms"]

        # Now, build metric from the counts dict
        table_data = [[i[0], round(np.mean(i[1]), 2)] for i in dataset_rms.items()]
        # Add header row
        table_data.insert(0, ["Task Type", "Dataset RMS (adu / sec)"])
        return self._create_table_metric(
            name="Dataset RMS",
            description="This metric is the calculated root mean square intensity value across data"
            " from an instrument program task type used in the creation of an entire "
            "L1 dataset.",
            rows=table_data,
            warnings=None,
        )

    def quality_store_historical(self, name: str, value: Any, warning: Optional[str] = None):
        """
        Insert historical data into the schema used to record quality info.

        Parameters
        ----------
        name: name of the parameter / measurement to be recorded
        value: value of the parameter / measurement to be recorded
        warning: warning to be entered into the quality report
        """
        data = {"name": name, "value": value, "warnings": warning}
        self._record_values(values=data, tags=Tag.quality("HISTORICAL"))

    def quality_build_historical(self) -> dict:
        """Build historical data schema from stored data."""
        table_data = []
        warnings = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("HISTORICAL")):
            with path.open() as f:
                data = json.load(f)
                table_data.append([data["name"], data["value"]])
                if data["warnings"] is not None:
                    warnings.append(data["warnings"])

        # Add header row
        table_data.insert(0, ["Metric", "Value"])
        return self._create_table_metric(
            name="Historical Comparisons",
            description="Over time, the data center will be comparing some of the above quality "
            "metrics and other parameters derived from file headers to see how the "
            "DKIST instruments and observations are changing.",
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )


class _PolcalQualityMixin:
    """Mixin Class supporting the building of polcal-specific metrics."""

    # TODO: Test coverage of this. Hard to do because a valid and realistic PolcalFItter is needed, which is tough
    #  Currently this is only tested in instrument Grogu tests
    def quality_store_polcal_results(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bins_1: int,
        bins_2: int,
        bin_1_type: str,
        bin_2_type: str,
    ):
        """Compute and store all PolCal related metrics."""
        logging.info("Storing global parameter values")
        self._store_polcal_global_parameter_values(polcal_fitter=polcal_fitter, label=label)

        logging.info("Storing local parameter values")
        self._store_polcal_local_parameter_values(
            polcal_fitter=polcal_fitter,
            label=label,
            bins_1=bins_1,
            bins_2=bins_2,
            bin_1_type=bin_1_type,
            bin_2_type=bin_2_type,
        )

        logging.info("Storing fit residuals")
        self._store_polcal_fit_resdiuals(
            polcal_fitter=polcal_fitter,
            label=label,
            bins_1=bins_1,
            bins_2=bins_2,
            bin_1_type=bin_1_type,
            bin_2_type=bin_2_type,
        )

        logging.info("Storing modulation matrix efficiencies")
        self._store_polcal_modulation_efficiency(
            polcal_fitter=polcal_fitter,
            label=label,
            bins_1=bins_1,
            bins_2=bins_2,
            bin_1_type=bin_1_type,
            bin_2_type=bin_2_type,
        )

    def _store_polcal_global_parameter_values(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
    ) -> None:
        """Compute and store best-fit polcal parameter statistics.

        Namely, the fit value and it's absolute and relative deviation from database metrology values.
        """
        init_pars = polcal_fitter.global_objects.init_parameters.first_parameters
        fit_pars = polcal_fitter.global_objects.fit_parameters.first_parameters

        # Record the values and diffs
        param_names = []
        param_vary = []
        param_init_vals = []
        param_fit_vals = []
        param_diffs = []
        param_ratios = []
        warnings = []
        for param, init_val in init_pars.valuesdict().items():
            # All parameter names are internally labeled with what Calibration Sequence (CS) they come from.
            #  Here we remove that label because we only care about the base name and these metrics only apply
            #  to data from single-CS fits.
            base_name = param.split("_CS")[0]
            if base_name not in GLOBAL_PARAMS and base_name not in CU_PARAMS:
                # Not a global parameter, so we don't need to analyze it.
                continue

            best_fit_val = fit_pars[param].value
            if base_name in ["ret0h", "ret045", "ret0r"]:
                # One of the 3 elliptical retardance parameters.
                base_name += (
                    " [deg]"  # Units are degrees, so add that to what's shown in the table.
                )
                init_val = np.rad2deg(init_val)  # ...and convert from radians
                best_fit_val = np.rad2deg(best_fit_val)

            param_names.append(base_name)
            param_vary.append(init_pars[param].vary)
            param_init_vals.append(init_val)
            param_fit_vals.append(best_fit_val)
            diff = init_val - best_fit_val
            if base_name in ["ret0h", "ret045", "ret0r"] and abs(diff) > 3.0:
                # Retardance values should be within 3 deg of the db value
                warnings.append(
                    f"{base_name.replace(' [deg]', '')} fit value deviates from the initial value by a large amount ({diff:.2f} degrees)"
                )

            if base_name in ["t_pol", "t_ret"] and abs(diff) > 0.05:
                # Optic transmission values should be within 5% of the db value
                warnings.append(
                    f"{base_name} fit value deviates from the initial value by a large amount ({abs(diff) * 100:.2f}%)"
                )
            param_diffs.append(diff)
            ratio = np.abs(diff) / init_val

            # NaN's look weird in a table. Replace with "-" instead.
            if np.isnan(ratio) or np.isinf(ratio):
                ratio = "-"
            param_ratios.append(ratio)

        data = {
            "task_type": label,
            "param_names": param_names,
            "param_vary": param_vary,
            "param_init_vals": param_init_vals,
            "param_fit_vals": param_fit_vals,
            "param_diffs": param_diffs,
            "param_ratios": param_ratios,
            "warnings": warnings,
        }
        self._record_values(
            values=data, tags=[Tag.quality("POLCAL_GLOBAL_PAR_VALS"), Tag.quality_task(label)]
        )

    def quality_build_polcal_global_parameter_values(self, label: str) -> dict:
        """Build Polcal parameter value table schema from stored data."""
        # This *could* exist in the _TableQualityMixin because it is just a simple table, but it's kept here because
        # it's corresponding store* method needs to be here for calling from the top-level quality_store_polcal_results
        data_file = next(
            self.read(tags=[Tag.quality("POLCAL_GLOBAL_PAR_VALS"), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        table_data = [
            [
                "Parameter",
                "Free in Fit?",
                "Init Value",
                "Best Fit Value",
                "Difference",
                "Relative Diff.",
            ]
        ]
        for pn, pv, pi, pfv, pd, pr in zip(
            data["param_names"],
            data["param_vary"],
            data["param_init_vals"],
            data["param_fit_vals"],
            data["param_diffs"],
            data["param_ratios"],
        ):
            try:
                pi_str = f"{pi: 6.2f}"
            except ValueError:
                pi_str = str(pi)
            try:
                pfv_str = f"{pfv: 6.2f}"
            except ValueError:
                pfv_str = str(pfv)
            try:
                pd_str = f"{pd: .2e}"
            except ValueError:
                pd_str = str(pd)
            try:
                pr_str = f"{pr: .2e}"
            except ValueError:
                pr_str = str(pr)
            table_data.append([pn, pv, pi_str, pfv_str, pd_str, pr_str])

        metric = ReportMetric(
            name=f"PolCal Global Calibration Unit Fit - {label}",
            description="The deviation from database metrology values for Calibration Unit parameters used to compute "
            f"demodulation matrices. These parameters are fit the same across all polcal bins.",
            table_data=SimpleTable(rows=table_data),
            warnings=self._format_warnings(data["warnings"]),
        )
        return metric.dict()

    def _store_polcal_local_parameter_values(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bins_1: int,
        bins_2: int,
        bin_1_type: str,
        bin_2_type: str,
    ) -> None:
        """Store local polcal parameter fits.

        First, flatten FOV bins dimensions, compute modulation matrices, and record I_sys for all bins.

        Then convert to python lists for serialization and write to disk.
        """
        ## Modulation matrices
        fov_shape = polcal_fitter.local_objects.dresser.shape
        num_mod = polcal_fitter.local_objects.dresser.nummod
        flattened_demod = np.reshape(
            polcal_fitter.demodulation_matrices, (np.prod(fov_shape), 4, num_mod)
        )
        flattened_mod = np.zeros((np.prod(fov_shape), num_mod, 4))
        for i in range(flattened_demod.shape[0]):
            flattened_mod[i] = np.linalg.pinv(flattened_demod[i])

        # Move axis so numpoints is the last dimension, which will be easier to understand when
        # plotting
        flattened_mod = np.moveaxis(flattened_mod, 0, -1)

        # Because ndarrays can't be Json'd
        mod_list = flattened_mod.tolist()

        ## I_sys
        I_sys_list = []
        for point_params in polcal_fitter.local_objects.fit_parameters._all_parameters:
            I_sys_list.append(point_params["I_sys_CS00"].value)

        # Get the starting value of I_sys, which is just I_clear
        # Take the first element because this is a Polcal (not Groupcal) and so there is only
        # a single Drawer
        I_sys_init = polcal_fitter.local_objects.dresser.I_clear[0]

        data = {
            "task_type": label,
            "bin_1_str": f"{bins_1} {bin_1_type}",
            "bin_2_str": f"{bins_2} {bin_2_type}",
            "total_bins": bins_1 * bins_2,
            "modmat_list": mod_list,
            "I_sys_list": I_sys_list,
            "I_sys_init": I_sys_init,
        }
        self._record_values(
            values=data, tags=[Tag.quality("POLCAL_LOCAL_PAR_VALS"), Tag.quality_task(label)]
        )

    def quality_build_polcal_local_parameter_values(self, label: str) -> dict:
        """Build a modulation matrix and I_sys histograms schema from stored data."""
        data_file = next(
            self.read(tags=[Tag.quality("POLCAL_LOCAL_PAR_VALS"), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        modmat_hist = ModulationMatrixHistograms(modmat_list=data["modmat_list"])
        I_sys_hist = PlotHistogram(
            xlabel="I_sys",
            series_data={"I_sys": data["I_sys_list"]},
            vertical_lines={"I_clear": data["I_sys_init"]},
        )
        metric = ReportMetric(
            name=f"PolCal Local Bin Fits - {label}",
            description=f"The first panel shows histograms of the individual modulation matrix elements. "
            "Note that the first element is not shown because it is always fixed to 1 in fits. "
            "The second shows the corresponding fits of I_sys, the overall flux scaling. "
            f"There are {data['total_bins']} samples spanning {data['bin_1_str']} "
            f"and {data['bin_2_str']} bins.",
            modmat_data=modmat_hist,
            histogram_data=I_sys_hist,
        )
        return metric.dict()

    def _store_polcal_fit_resdiuals(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bins_1: int,
        bins_2: int,
        bin_1_type: str,
        bin_2_type: str,
    ):
        """Store flux residuals and chisq values for a local fit."""
        fit_container = polcal_fitter.local_objects
        fov_shape = fit_container.dresser.shape
        num_mod = fit_container.dresser.nummod
        num_steps = fit_container.dresser.numsteps
        num_points = np.prod(fov_shape)
        residual_array = np.zeros((num_mod, num_steps, num_points))
        red_chi_list = []
        for i in range(num_points):
            ## Fit residuals
            point_TM = copy.deepcopy(fit_container.telescope)
            point_CM = copy.deepcopy(fit_container.calibration_unit)

            idx = np.unravel_index(i, fov_shape)
            I_cal, I_unc = fit_container.dresser[idx]
            fit_params = fit_container.fit_parameters[idx]
            modmat = np.zeros((I_cal.shape[0], 4), dtype=np.float64)
            flat_residual = compare_I(
                params=fit_params,
                I_cal=I_cal,
                I_unc=I_unc,
                TM=point_TM,
                CM=point_CM,
                modmat=modmat,
                use_M12=True,
            )
            diff = np.reshape(flat_residual, (num_mod, num_steps))
            residual_array[:, :, i] = diff

            ## Red Chisq
            chisq = np.sum(flat_residual**2)
            num_free = sum([fit_params[p].vary for p in fit_params])
            red_chisq = chisq / num_free
            red_chi_list.append(red_chisq)

        # Convert residuals to panda DataFrame, which will greatly simplify plotting
        col_list = sum(
            [
                [[r, i + 1, j + 1] for r in residual_array[i, j, :]]
                for i in range(num_mod)
                for j in range(num_steps)
            ],
            [],
        )
        residual_dataframe = DataFrame(
            data=col_list, columns=["Flux residual", "Modstate", "CS Step"]
        )
        dataframe_str = residual_dataframe.to_json()

        data = {
            "task_type": label,
            "bin_1_str": f"{bins_1} {bin_1_type}",
            "bin_2_str": f"{bins_2} {bin_2_type}",
            "total_bins": bins_1 * bins_2,
            "residual_json": dataframe_str,
            "red_chi_list": red_chi_list,
        }
        self._record_values(
            values=data, tags=[Tag.quality("POLCAL_FIT_RESIDUALS"), Tag.quality_task(label)]
        )

    def quality_build_polcal_fit_residuals(self, label: str) -> dict:
        """Build a metric containing flux residuals and reduced chisq values for all fits.

        The chisq values will turn into a histogram and the flux residuals will turn into a very fancy
        violin plot.
        """
        data_file = next(
            self.read(tags=[Tag.quality("POLCAL_FIT_RESIDUALS"), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        chisq = data["red_chi_list"]
        avg_chisq = np.mean(chisq)
        chisq_hist = PlotHistogram(
            xlabel="Reduced Chisq",
            series_data={"Red chisq": chisq},
            vertical_lines={f"Mean = {avg_chisq:.2f}": avg_chisq},
        )
        residual_series = PlotRaincloud(
            xlabel="CS Step",
            ylabel=r"$\frac{I_{fit} - I_{obs}}{\sigma_I}$",
            ylabel_horizontal=True,
            categorical_column_name="CS Step",
            distribution_column_name="Flux residual",
            hue_column_name="Modstate",
            dataframe_json=data["residual_json"],
        )
        metric = ReportMetric(
            name=f"PolCal Fit Residuals - {label}",
            description="The top plot shows relative flux residual distributions for all polcal Calibration Sequence "
            "steps. The bottom plot shows the reduced chi-squared distribution of all fits. "
            f"Data show {data['total_bins']} total samples spanning {data['bin_1_str']} "
            f"and {data['bin_2_str']} bins.",
            histogram_data=chisq_hist,
            raincloud_data=residual_series,
        )
        return metric.dict()

    def _store_polcal_modulation_efficiency(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bins_1: int,
        bins_2: int,
        bin_1_type: str,
        bin_2_type: str,
    ):
        """Compute modulation efficiency for all fit bins and store in a file."""
        fov_shape = polcal_fitter.local_objects.dresser.shape
        num_mod = polcal_fitter.local_objects.dresser.nummod
        num_points = np.prod(fov_shape)
        flat_demod = np.reshape(polcal_fitter.demodulation_matrices, (num_points, 4, num_mod))
        flat_efficiency = 1.0 / np.sqrt(
            num_mod * np.sum(flat_demod**2, axis=2)
        )  # (num_points, 4)

        # Because ndarrays are not JSON-able
        # Also, transpose it so the Stokes parameters are the first dimension
        efficiency_list = flat_efficiency.T.tolist()

        warnings = []
        stokes_names = ["I", "Q", "U", "V"]
        efficiency_thresholds = [0.8, 0.4, 0.4, 0.4]
        means = np.mean(flat_efficiency, axis=0)
        for i, (stokes, thresh) in enumerate(zip(stokes_names, efficiency_thresholds)):
            if means[i] < thresh:
                warnings.append(
                    f"Stokes {stokes} has a low mean efficiency ({means[i] * 100:.1f} %)"
                )
        data = {
            "task_type": label,
            "bin_1_str": f"{bins_1} {bin_1_type}",
            "bin_2_str": f"{bins_2} {bin_2_type}",
            "total_bins": bins_1 * bins_2,
            "efficiency_list": efficiency_list,
            "warnings": warnings,
        }
        self._record_values(
            values=data, tags=[Tag.quality("POLCAL_EFFICIENCY"), Tag.quality_task(label)]
        )

    def quality_build_polcal_efficiency(self, label: str) -> dict:
        """Build a metric containing samples of the modulation efficiency for each stokes parameter."""
        data_file = next(
            self.read(tags=[Tag.quality("POLCAL_EFFICIENCY"), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        metric = ReportMetric(
            name=f"PolCal Modulation Efficiency - {label}",
            description="The modulation efficiencies for all fit modulation matrices. "
            f"Data show {data['total_bins']} total samples spanning {data['bin_1_str']} "
            f"and {data['bin_2_str']} bins.",
            efficiency_data=EfficiencyHistograms(efficiency_list=data["efficiency_list"]),
            warnings=self._format_warnings(data["warnings"]),
        )
        return metric.dict()
