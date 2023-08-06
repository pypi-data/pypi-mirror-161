from __future__ import annotations
import os
import time
import textwrap
import deprecation  # type: ignore
from urllib.parse import urljoin
import posixpath
import json
from . import public_api_pb2 as api_pb
from . import public_rest_api as api
from . import api_status_codes
from .public_rest_api import ClientConfig, Device, Shapes
from typing import List, Union, Optional, Dict, cast
from dataclasses import dataclass
import tempfile
from datetime import datetime
from collections import OrderedDict
from enum import Enum


def _profile_pb_to_python_dict(profile_pb: api_pb.ProfileDetail) -> dict:
    layer_details = []
    for layer_detail_pb in profile_pb.layer_details:
        layer_details.append(
            {
                "name": layer_detail_pb.name,
                "type": layer_detail_pb.layer_type_name,
                "compute_unit": api_pb.ComputeUnit.Name(layer_detail_pb.compute_unit),
            }
        )

    return {
        "execution_summary": {
            "execution_time": profile_pb.execution_time,
            "load_time": profile_pb.load_time,
            "peak_memory_usage": profile_pb.peak_memory_usage,
        },
        "execution_detail": layer_details,
    }


def _class_repr_print(obj, fields):
    """
    Display a class repr according to some simple rules.

    Parameters
    ----------
    obj: Object to display a repr for
    fields: List of Union[str | (str, str)]
    """

    # Record the max_width so that if width is not provided, we calculate it.
    max_width = len("Class")

    # Add in the section header.
    section_title = obj.__class__.__name__
    out_fields = [section_title, "-" * len(section_title)]

    # Add in all the key-value pairs
    for f in fields:
        if type(f) == tuple:
            out_fields.append(f)
            max_width = max(max_width, len(f[0]))
        else:
            out_fields.append((f, getattr(obj, f)))
            max_width = max(max_width, len(f))

    # Add in the empty footer.
    out_fields.append("")

    # Now, go through and format the key_value pairs nicely.
    def format_key_pair(key, value):
        return key.ljust(max_width, " ") + " : " + str(value)

    out_fields = [s if type(s) == str else format_key_pair(*s) for s in out_fields]
    return "\n".join(out_fields)


## ERROR HANDLING ##
class Error(Exception):
    """
    Base class for all exceptions explicitly thrown by the API.

    Other exception may be raised from dependent third party packages.
    """

    def __init__(self, message):
        super().__init__(message)


class InternalError(Error):
    """
    Internal API failure; please contact support@tetra.ai for assistance.
    """

    def __init__(self, message):
        super().__init__(message)


class UserError(Error):
    """
    Something in the user input caused a failure; you may need to adjust your input.
    """

    def __init__(self, message):
        super().__init__(message)


def _visible_textbox(text):
    """
    Letting exceptions terminate a python program is a cluttered way to give
    user feedback. This box is to draw attention to action items for users.
    """
    width = 70
    text = textwrap.dedent(text).strip()
    wrapper = textwrap.TextWrapper(width=width - 4)
    header = "┌" + "─" * (width - 2) + "┐\n"
    footer = "\n└" + "─" * (width - 2) + "┘"

    lines = ["| " + line.ljust(width - 4) + " |" for line in wrapper.wrap(text)]
    return header + "\n".join(lines) + footer


def _api_call(api_func, *args, **kwargs):
    """
    Wrapper to re-raise the most common API exceptions appriopriate for the
    client.
    """
    try:
        return api_func(*args, **kwargs)
    except api.APIException as e:
        config_path = api.get_config_path(expanduser=False)
        if e.status_code == api_status_codes.HTTP_404_NOT_FOUND:
            raise UserError(str(e))
        elif e.status_code == api_status_codes.HTTP_401_UNAUTHORIZED:
            long_message = _visible_textbox(
                "Failure to authenticate is likely caused by a bad or outdated API "
                f"token in your {config_path} file. Please go to your Account page "
                "to view your current token."
            )

            raise UserError(f"Failed to authenticate.\n{long_message}")
        elif e.status_code == api_status_codes.API_CONFIGURATION_MISSING_FIELDS:
            long_message = _visible_textbox(
                f"Your {config_path} file is missing required fields. "
                "Please go to your Account page to see an example."
            )

            raise UserError(f"Failed to load configuration file.\n{long_message}")
        elif e.status_code == api_status_codes.HTTP_500_INTERNAL_SERVER_ERROR:
            long_message = _visible_textbox(
                "The error suggests that Tetra Hub is experiencing a service failure. "
                "Please contact support at support@tetra.ai."
            )

            raise InternalError(f"Internal API failure.\n{long_message}")
        else:
            # Re-raise, let the function catch it, or let it bubble up
            raise


## MODELS ##

SourceModel = Union[
    "torch.jit.TopLevelTracedModule",  # type: ignore # noqa: F821 (imported conditionally)
    "coremltools.models.model.MLModel",  # type: ignore # noqa: F821 (imported conditionally)
]

TargetModel = Union[
    "coremltools.models.model.MLModel",  # type: ignore # noqa: F821 (imported conditionally)
]


class SourceModelType(Enum):
    """
    Set of supported input model types.
    """

    TORCHSCRIPT = api_pb.ModelType.TORCHSCRIPT
    MLMODEL = api_pb.ModelType.MLMODEL


def _determine_model_type(model: Union[SourceModel, str]) -> SourceModelType:
    if isinstance(model, str):
        _, suffix = os.path.splitext(model)
        if suffix == ".pt" or suffix == ".pth":
            return SourceModelType.TORCHSCRIPT
        elif suffix == ".mlmodel":
            return SourceModelType.MLMODEL
        else:
            if suffix == "":
                raise UserError(
                    rf"""Path "{model}" is a directory or has no extension, which is not supported. Two model types supported are:
                            * TorchScript : model path must have extension .pt or .pth"
                            * CoreML Model : model path must have extension .mlmodel """
                )
            raise UserError(
                rf"""Extension {suffix} is not supported. Two model types supported are:
                        * TorchScript : model path must have extension .pt or .pth
                        * CoreML Model : model path must have extension .mlmodel"""
            )
    elif type(model).__name__ in {"TopLevelTracedModule", "RecursiveScriptModule"}:
        return SourceModelType.TORCHSCRIPT
    elif type(model).__name__ == "MLModel":
        return SourceModelType.MLMODEL
    else:
        module_name_list = [model_type.__module__ for model_type in type(model).mro()]
        if "torch.nn.modules.module" in module_name_list:
            raise UserError("The torch model must be traced.")
        raise UserError(
            r"""Unsupported model type. The supported model types are:
                    * Traced TorchScript model
                    * CoreML model """
        )


class Model:
    """
    Neural network model object.

    A model should not be constructed directly. It is constructed by the hub client
    through :py:func:`tetra_hub.upload_model`, :py:func:`tetra_hub.get_model`, or
    :py:func:`tetra_hub.get_models`.

    Attributes
    ----------
    model_id : str
        The model ID.
    date : datetime
        The time this model was uploaded.
    model_type : SourceModelType
        The type of the model.
    name : str
        An optional user-provided name to identify the model.

    """

    def __init__(
        self,
        owner: Client,
        model_id: str,
        date: datetime,
        model_type: SourceModelType,
        name: str,
        model: Optional[SourceModel],
        verbose: bool,
    ):
        self._owner = owner
        self.model_id = model_id
        self.date = date
        self.model_type = model_type
        self.name = name
        self._model = model  # access through download_model
        self.verbose = verbose

    def download_model(self, filename: Optional[str] = None) -> Union[SourceModel, str]:
        """
        Downloads source model either to memory or to file.

        Parameters
        ----------
        filename : Optional[str]
            If filename is specified the model is downloaded to file, otheriwse to memory.

        Returns
        -------
        : SourceModel | str
            Loaded model instance or file name. The returned type depends on the model type.
        """
        if self._model is None:
            to_file = filename is not None
            if filename is None:
                with tempfile.NamedTemporaryFile() as f:
                    download_file = f.name
            else:
                download_file = filename
            filename = _api_call(
                api.download_model,
                self.model_id,
                download_file,
                verbose=self.verbose,
                config=self._owner._config,
            )
            if to_file:
                return filename
            elif self.model_type == SourceModelType.TORCHSCRIPT:
                import torch

                self._model = torch.jit.load(filename)
            elif self.model_type == SourceModelType.MLMODEL:
                import coremltools

                self._model = coremltools.models.MLModel(filename)
            return self._model
        else:
            if filename is None:
                return self._model
            if os.path.isdir(filename):
                # Grab filename from the API and append it to the path.
                model_info = api.download_model_info(self.model_id, self._owner._config)
                filename = os.path.join(filename, model_info.filename)

            if self.model_type == SourceModelType.TORCHSCRIPT:
                import torch

                torch.jit.save(self._model, filename)
            elif self.model_type == SourceModelType.MLMODEL:
                import coremltools

                self._model.save(filename)
            return filename

    def __str__(self) -> str:
        return f"Model(model_id={self.model_id}, name={self.name})"

    def __repr__(self) -> str:
        return _class_repr_print(
            self, ["model_id", "name", ("model_type", self.model_type.name), "date"]
        )


## JOBS ##


@dataclass
class JobStatus:
    """
    Status of a job.

    Attributes
    ----------
    code: str
        Status code for the job. Valid codes are "SUCCESS", "FAILED", "UNKNOWN",
        OPTIMIZING_MODEL", "WAITING_FOR_DEVICE", and "MEASURING_PERFORMANCE"
    message: str
        Optional error message.
    """

    code: str
    message: Optional[str] = None

    @property
    def success(self) -> bool:
        """
        Returns whether a job finished succesfully.

        Returns
        -------
        : bool
            returns true if the job finished succesfully.
        """
        return self.code == "SUCCESS"

    @property
    def failure(self) -> bool:
        """
        Returns whether a job failed.

        Returns
        -------
        : bool
            returns true if the job failed.
        """
        return self.code == "FAILED"

    @property
    def finished(self) -> bool:
        """
        Returns whether a job finished.

        Returns
        -------
        : bool
            returns true if the job finished.
        """
        return self.success or self.failure

    @property
    def running(self) -> bool:
        """
        Returns whether a job is still riunning.

        Returns
        -------
        : bool
            returns true if the job is still running.
        """
        return not self.finished

    def __eq__(self, obj):
        if isinstance(obj, str):
            return self.code == obj
        return self.code == obj.code and self.message == obj.message

    def __repr__(self):
        return _class_repr_print(self, ["code", "message"])


@dataclass
class JobResult:
    # TODO: Have the output below be produced by doctest
    """
    Job result structure.

    Attributes
    ----------
    status : JobStatus
        Status of the job.
    profile : Dict
        The profile result as a python dictionary for a successful job.
    artifacts_dir : str
        A user-provided directory name where artifacts will be stored.
        When set to None, no additional artifacts are downloaded.

    Examples
    --------
    Fetch a job result::

        >>> import tetra_hub as hub
        >>> job = hub.get_jobs()[0]
        >>> job_result = job.download_results()

    Print the profiling results as a dictionary structure::

        >>> print(job_result.profile)
        { ... }

    Print the model runtime latency in milliseconds::

        >>> latency_ms = job_result.profile["execution_summary"]["execution_time"] / 1000
        >>> print("Latency: {latency_ms:.1f} ms")
        0.6 ms
    """

    status: JobStatus
    url: str
    profile: Dict
    artifacts_dir: Optional[str] = None

    @property
    def _compute_unit_breakdown(self):
        breakdown = OrderedDict([("NPU", 0), ("GPU", 0), ("CPU", 0)])
        for layer_detail in self.profile["execution_detail"]:
            breakdown[layer_detail["compute_unit"]] += 1
        return breakdown

    def __repr__(self):
        # Successful job
        if self.status.success:
            profile_sum = self.profile["execution_summary"]
            breakdown = self._compute_unit_breakdown
            breakdown_str = ", ".join(
                f"{k}: {v}" for k, v in breakdown.items() if v > 0
            )
            return _class_repr_print(
                self,
                [
                    "url",
                    ("Execution Time (ms)", profile_sum["execution_time"] / 1000),
                    ("Load Time (ms)", profile_sum["load_time"] / 1000),
                    (
                        "Peak Memory (MB)",
                        profile_sum["peak_memory_usage"] / 1024 / 1024,
                    ),
                    ("Compute Units (layers)", breakdown_str),
                ],
            )
        # Failed job
        else:
            return _class_repr_print(self, ["status", "url"])


class Job:
    """
    Profiling job for a model, a set of input shapes, and a device.

    A job should not be constructed directly. It is constructed by the hub client
    through :py:func:`tetra_hub.submit_profile_job`, :py:func:`tetra_hub.get_job`, or
    :py:func:`tetra_hub.get_jobs`.

    Attributes
    ----------
    job_id : str
        The job ID.
    device : Device
        The device for this job.
    model : Model
        The model for the job.
    name : str
        Name of this job
    date : datetime
        The time this job was submitted.
    shapes : Shapes
        The input shapes for the model.
    options: str
        Options passed during the job submission.
    """

    _polling_interval: int = 10

    def __init__(
        self,
        owner: Client,
        job_id: str,
        device: Device,
        model: Model,
        name: str,
        date: datetime,
        shapes: Shapes,
        options: str,
        verbose: bool,
    ):
        self._owner = owner
        self.job_id = job_id
        self.device = device
        self.model = model
        self.name = name
        self.date = date
        self.shapes = shapes
        self.options = options
        self.verbose = verbose

    @property
    def url(self):
        """
        Returns the URL for the job.

        Returns
        -------
        : str
            The URL for the job.
        """

        return f"{self._owner._web_url_of_job(self.job_id)}"

    def get_status(self) -> JobStatus:
        """
        Returns the status of a job.

        Returns
        -------
        : JobStatus
            The status of the job
        """
        job_pb = _api_call(api.get_profile_job, self.job_id, config=self._owner._config)
        error_map: Dict[api_pb.ProfileJobState.ValueType, str] = {
            api_pb.ProfileJobState.DONE: "SUCCESS",
            api_pb.ProfileJobState.FAILED: "FAILED",
            api_pb.ProfileJobState.UNDEFINED: "UNKNOWN",
            api_pb.ProfileJobState.OPTIMIZING_MODEL: "OPTIMIZING_MODEL",
            api_pb.ProfileJobState.WAITING_FOR_DEVICE: "WAITING_FOR_DEVICE",
            api_pb.ProfileJobState.MEASURING_PERFORMANCE: "MEASURING_PERFORMANCE",
        }
        return JobStatus(error_map[job_pb.job_state], job_pb.failure_reason)

    def _wait(self) -> JobStatus:
        status = self.get_status()
        while status.running:
            time.sleep(Job._polling_interval)
            status = self.get_status()
        return status

    def _write_profile(self, profile: Dict, filename: str) -> str:
        """
        Saves the profile json to disk.

        Parameters
        ----------
        filename :
            Dir or filename to save to.

        Returns
        -------
        : str
            The path of the saved profile json.
        """
        filename = os.path.expanduser(filename)  # Resolve ~ to user dir

        if os.path.isdir(filename):
            # Append a reasonable filename to save to.
            filename = os.path.join(filename, f"{self.name}_{self.job_id}_results.json")

        with open(filename, "w") as file:
            json.dump(profile, file)
        return filename

    def download_profile(self, filename: Optional[str] = None) -> Union[Dict, str]:
        """
        Returns the downloaded profile, either in memory or as a file.

        If the job is not ready, this function will block until completion.

        Parameters
        ----------
        filename : Optional[str]
            If filename is specified the profile is downloaded to file, otheriwse to memory.

        Returns
        -------
        : Union[Dict, str]
            The downloaded profile, or filename
        """
        status = self._wait()
        profile = {}
        if status.success:
            res_pb = _api_call(
                api.get_profile_job_results, self.job_id, config=self._owner._config
            )
            profile = _profile_pb_to_python_dict(res_pb.profile)
            if filename is not None:
                return self._write_profile(profile, filename)

        return profile

    def download_target_model(
        self, filename: Optional[str] = None
    ) -> Optional[Union[TargetModel, str]]:
        """
        Returns the downloaded target model, either in memory or as a file.

        If the job is not ready, this function will block until completion.

        Parameters
        ----------
        filename : Optional[str]
            If filename is specified the target model is downloaded to file, otheriwse to memory.

        Returns
        -------
        : Optional[Union[TargetModel, str]]
            The downloaded target model, filename, or None if the job failed.
        """

        status = self._wait()
        if status.success:
            to_file = filename is not None
            if not to_file:
                with tempfile.NamedTemporaryFile(suffix=".mlmodel") as file:
                    filename = file.name
            filename = _api_call(
                api.download_compiled_model,
                self.job_id,
                file_path=filename,
                verbose=self.verbose,
                config=self._owner._config,
            )
            if to_file:
                return filename
            else:
                import coremltools

                return coremltools.models.MLModel(filename)
        return None

    def download_results(self, artifacts_dir: str) -> JobResult:
        """
        Returns all the results of a job.

        This includes the profile and the compiled target model.
        With exception of the profile, all other results are placed
        in the artifacts_dir directory.

        If the job is not ready, this function will block until completion.

        Parameters
        ----------
        artifacts_dir : str
            Directory name where the job artifacts are stored.

        Returns
        -------
        : JobResult
            Job results.
        """
        if artifacts_dir is None:
            raise UserError("must provide a valid directory to store artifacts.")

        profile = self.download_profile()

        os.makedirs(artifacts_dir, exist_ok=True)
        self.download_target_model(artifacts_dir)
        self._write_profile(profile, artifacts_dir)  # type: ignore

        return JobResult(
            status=self.get_status(),
            url=self.url,
            profile=cast(Dict, profile),
            artifacts_dir=artifacts_dir,
        )

    @deprecation.deprecated(
        details="Please use one of \
               'download_profile', 'download_target_model', or 'download_results' instead."
    )
    def get_results(self, artifacts_dir: Optional[str] = None) -> JobResult:
        profile = self.download_profile()
        if artifacts_dir is not None:
            mlmodel = os.path.join(artifacts_dir, "target.mlmodel")
            self.download_target_model(mlmodel)

        return JobResult(
            status=self.get_status(),
            url=self.url,
            profile=cast(Dict, profile),
            artifacts_dir=artifacts_dir,
        )

    def __str__(self) -> str:
        return f"Job(job_id={self.job_id}, model_id={self.model.model_id}, device={self.device}"

    def __repr__(self) -> str:
        return _class_repr_print(
            self,
            [
                "job_id",
                "url",
                ("status", self.get_status().code),
                "model",
                "name",
                "shapes",
                "device",
                "date",
            ],
        )


class Client:
    """
    Client object to interact with the Tetra Hub API.

    A default client, using credentials from ``~/.tetra/client.ini`` can be
    accessed through the ``tetra_hub`` module::

        import tetra_hub as hub

        # Calls Client.upload_model on a default Client instance.
        hub.upload_model("model.pt")
    """

    # Note: This class is primarily used through a default instantiation
    # through hub (e.g. import tetra_hub as hub; hub.upload_model(...)). For that
    # reason, all examples and cross references should point to tetra_hub for
    # documentation generation purposes.

    def __init__(self, config: ClientConfig = None, verbose: bool = False):
        self._config = config
        self.verbose = verbose
        self.fetch_devices = True

    @property
    def config(self):
        if self._config is None:
            try:
                self._config = _api_call(api.utils.load_default_api_config)
            except FileNotFoundError as e:
                raise UserError(
                    "Failed to load client configuration file.\n"
                    + _visible_textbox(str(e))
                )
        return self._config

    @staticmethod
    def _date_from_timestamp(pb) -> datetime:
        return datetime.fromtimestamp(pb.creation_time.seconds)

    def _web_url_of_job(self, job_id: str):
        # Final empty '' is to produce a trailing slash (esthetic choice)
        return urljoin(self.config.web_url, posixpath.join("jobs", job_id, ""))

    def set_verbose(self, verbose: bool = True):
        """
        If true, API calls may print progress to standard output.

        Parameters
        ----------
        verbose : bool
            Verbosity.

        """
        self.verbose = verbose

    def get_devices(self) -> List[Device]:
        """
        Returns a list of available devices.

        Returns
        -------
        device_list : List[Device]
            List of available devices.

        Examples
        --------
        ::

            import tetra_hub as hub

            devices = hub.get_devices()
            print(devices)
        """
        if self.fetch_devices:
            self._devices = []
            devices_pb = _api_call(api.get_device_list, config=self.config)
            for dev in devices_pb.devices:
                self._devices.append(Device(dev.name, dev.os))
            self.fetch_devices = False
        return self._devices

    ## model related members ##
    def _make_model(
        self, model_pb: api_pb.Model, model: Optional[SourceModel] = None
    ) -> Model:
        date = self._date_from_timestamp(model_pb)
        return Model(
            self,
            model_pb.model_id,
            date,
            SourceModelType(model_pb.model_type),
            model_pb.name,
            model,
            self.verbose,
        )

    def _upload_model(
        self,
        model: Union[SourceModel, str],
        model_type: SourceModelType,
        name: Optional[str] = None,
    ) -> Model:
        if isinstance(model, str):
            path = model
            model_name = name or model
            model = None
        elif model_type == SourceModelType.TORCHSCRIPT:
            with tempfile.NamedTemporaryFile(suffix=".pt") as file:
                path = file.name
            import torch

            torch.jit.save(model, path)
            model_name = name or model.original_name

        elif model_type == SourceModelType.MLMODEL:
            with tempfile.NamedTemporaryFile(suffix=".mlmodel") as file:
                path = file.name
            model.save(path)
            # TODO: Figure out a better default name for MLModel instances
            model_name = name or "MLModel"

        api_model_type = api_pb.ModelType.ValueType(model_type.value)
        res_pb = _api_call(
            api.upload_model,
            path,
            name=model_name,
            model_type=api_model_type,
            config=self.config,
            verbose=self.verbose,
        )

        if res_pb.id:
            model_pb = api_pb.Model(
                model_id=res_pb.id,
                name=model_name,
                creation_time=res_pb.creation_time,
                model_type=api_model_type,
            )
            return self._make_model(model_pb, model)

        raise InternalError("Failed to upload model.")

    def upload_model(
        self, model: Union[SourceModel, str], name: Optional[str] = None
    ) -> Model:
        """
        Uploads a model.

        Parameters
        ----------
        model : SourceModel | str
            In memory representation or filename of the model to upload.
        name : Optional[str]
            Optional name of the model. If a name is not specified, it is decided
            either based on the model or the file name.

        Returns
        -------
        model : Model
            Returns a model if successful.

        Raises
        ------
        UserError
            Failure in the model input.

        Examples
        --------
        ::

            import tetra_hub as hub
            import torch

            pt_model = torch.jit.load("model.pt")

            # Upload model
            model = hub.upload_model(pt_model)

            # Jobs can now be scheduled using this model
            device = hub.Device("Apple iPhone 13 Pro", "15.2")
            job = hub.submit_profile_job(model, device=device,
                                         name="pt_model (1, 3, 256, 256)",
                                         input_shapes=[(1, 3, 256, 256)])

        """
        model_type = _determine_model_type(model)
        return self._upload_model(model, model_type, name)

    def get_model(self, model_id: int) -> Model:
        """
        Returns a model for a given id.

        Parameters
        ----------
        model_id : int
            id of a model.

        Returns
        -------
        model: Model
            The model for the id.
        """
        model_pb = _api_call(api.get_model, model_id=model_id, config=self.config)
        return self._make_model(model_pb)

    def get_models(self, offset: int = 0, limit: int = 50) -> List[Model]:
        """
        Returns a list of models.

        Parameters
        ----------
        offset : int
            Offset the query to get even older models.
        limit : int
            Maximum numbers of models to return.

        Returns
        -------
        model_list: List[Model]
            List of models.
        """
        models = []
        if limit > 0:
            model_list_pb = _api_call(
                api.get_model_list, offset=offset, limit=limit, config=self.config
            )
            for model_pb in model_list_pb.models:
                models.append(self._make_model(model_pb))
        return models

    ## job related members ##
    def _make_job(
        self, job_pb: api_pb.ProfileJob, model: Optional[Model] = None
    ) -> Job:
        model = model or self._make_model(job_pb.model)
        shapes = api.utils.tensor_type_list_pb_to_list_shapes(job_pb.tensor_type_list)
        date = self._date_from_timestamp(job_pb)
        device = Device(job_pb.device.name, job_pb.device.os)
        return Job(
            self,
            job_pb.profile_job_id,
            device,
            model,
            job_pb.name,
            date,
            shapes,
            job_pb.options,
            self.verbose,
        )

    def get_job(self, job_id: str) -> Job:
        """
        Returns a job for a given id.

        Parameters
        ----------
        job_id : str
            id of a job.

        Returns
        -------
        job: Job
            The job for the id.

        Examples
        --------
        Get job and print its status (this job ID may not work for you)::

            import tetra_hub as hub

            job = hub.get_job("rmg9lg7y")
            print("Status of job:", job.get_status().name)
        """
        job_pb = _api_call(api.get_profile_job, job_id=job_id, config=self.config)
        return self._make_job(job_pb)

    def get_jobs(self, offset: int = 0, limit: int = 50) -> List[Job]:
        """
        Returns a list of jobs visible to you.

        Parameters
        ----------
        offset : int
            Offset the query to get even older jobs.
        limit : int
            Maximum numbers of jobs to return.

        Returns
        -------
        job_list: List[Job]
            List of jobs.

        Examples
        --------
        Fetch :py:class:`JobResult` objects for your five most recent jobs::

            import tetra_hub as hub

            jobs = hub.get_jobs(limit=5)
            results = [job.download_results() for job in jobs]
        """
        jobs = []
        if limit > 0:
            job_list_pb = _api_call(
                api.get_profile_job_list, offset=offset, limit=limit, config=self.config
            )
            for job_pb in job_list_pb.jobs:
                jobs.append(self._make_job(job_pb))
        return jobs

    def submit_profile_job(
        self,
        model: Union[Model, SourceModel, str],
        device: Union[Device, List[Device]],
        name: Optional[str] = None,
        input_shapes: Optional[Shapes] = None,
        options: Optional[str] = None,
    ) -> Union[Job, List[Job]]:
        """
        Submits a profiling job.

        Parameters
        ----------
        model : Model | SourceModel | str
            Model to profile.
        devices : Device | List[Device]
            Devices on which to run the job.
        name : None | str
            Optional name for this job. This name does not uniquely define a job and different jobs can therefore share the same name.
        input_shapes : None | Dict[str, Tuple[int, ...]] | List[Tuple[int, ...]] | OrderedDict[str, Tuple[int, ...]]]] | List[Tuple[str, Tuple[int, ...]]]
            When the SourceModel is a PyTorch model, the input_shapes can be a list of tuples (one for each input) or an OrderedDict
            where the keys are the (optional) names of the features. These names are used for input nodes in the compiled CoreML model.
            Setting input_shapes to dictionary without ordering is not supported for PyTorch models.

            When the SourceModel is a CoreML model, the input_shapes can be set to None (inferred from the model) or a dict/OrderedDict,
            where the keys are the names of the features and values are the shapes. Setting input_shapes to List[Tuples] without names
            is not supported for CoreML models.
        options : None | str
            Additional options.

        Returns
        -------
        job: Job | List[Job]
            Returns the profile jobs.

        Examples
        --------
        Submit a traced Torch model for profiling on an iPhone 11::

            import tetra_hub as hub
            import torch

            pt_model = torch.jit.load("mobilenet.pt")

            input_shapes = (1, 3, 224, 224)

            model = hub.upload_model(pt_model)

            job = hub.submit_profile_job(model, device=hub.Device("Apple iPhone 11", "14.0"),
                                         name="mobilenet (1, 3, 224, 224)",
                                         input_shapes=[input_shapes])

        For more examples, see :ref:`examples`.
        """
        if isinstance(device, Device):
            device = [device]

        # Determine the model type
        if isinstance(model, Model):
            model_type = model.model_type
        else:
            model_type = _determine_model_type(model)

        if model_type == SourceModelType.TORCHSCRIPT:
            if input_shapes is None or not any(input_shapes):
                raise UserError("input_shapes must be provided for TorchScript models.")
            if not isinstance(input_shapes, OrderedDict) and not isinstance(
                input_shapes, list
            ):
                raise UserError(
                    "input_shapes for TorchScript models must be a List[Tuple[int, ...] or OrderedDict[str, Tuple[int, ...]] or List[Tuple[str, Tuple[int, ...]]]."
                )
        elif model_type == SourceModelType.MLMODEL:
            if (
                input_shapes is not None
                and isinstance(input_shapes, list)
                and any(input_shapes)
                and not isinstance(input_shapes[0][0], str)
            ):
                raise UserError("input_shapes must have names for model inputs.")

        if input_shapes is not None:
            tensor_type_list_pb = api.utils.list_shapes_to_tensor_type_list_pb(
                input_shapes
            )
        else:
            tensor_type_list_pb = None

        for dev in device:
            if dev not in self.get_devices():
                raise UserError(f"{dev} is not available.")

        if not isinstance(model, Model):
            model = self._upload_model(model, model_type=model_type)

        if name:
            job_name = name
        else:
            job_name = model.name

        jobs = []
        for dev in device:
            dev_pb = api_pb.Device(name=dev.name, os=dev.os)
            model_pb = api_pb.Model(model_id=model.model_id)
            job_pb = api_pb.ProfileJob(
                model=model_pb,
                name=job_name,
                device=dev_pb,
                tensor_type_list=tensor_type_list_pb,
                options=options if options else "",
            )
            response_pb = _api_call(api.create_profile_job, job_pb, config=self.config)
            job_pb.profile_job_id = response_pb.id
            job_pb.creation_time.CopyFrom(response_pb.creation_time)
            job = self._make_job(job_pb, model)
            jobs.append(job)
            if self.verbose:
                msg = (
                    f"Scheduled job ({job.job_id}) successfully. To see "
                    "the status and results:\n"
                    f"    {job.url}\n"
                )
                print(msg)

        return jobs[0] if len(jobs) == 1 else jobs


__all__ = [
    "Error",
    "InternalError",
    "UserError",
    "Device",
    "Model",
    "Job",
    "SourceModelType",
    "JobResult",
    "JobStatus",
    "Shapes",
]
