from __future__ import annotations

import curses
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Optional,
    Type,
    Union,
)

from deprogressapi.settings import ReportSettings, ShowReportMethod
from pydantic import BaseModel, Field, create_model

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal  # type: ignore
if TYPE_CHECKING:
    from pydantic.typing import ReprArgs

    from demessaging.PulsarMessageConsumer import PulsarMessageConsumer


class Status(str, Enum):

    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"


class BaseReport(BaseModel):
    """A base report for sending messages via pulsar."""

    class Config:
        underscore_attrs_are_private = True

    _pulsar: Optional[PulsarMessageConsumer] = None
    _request: Optional[Dict] = None
    _response_properties: Optional[Dict] = None
    _window: Optional[curses.window] = None  # type: ignore

    show_methods: ClassVar[Dict[ShowReportMethod, str]] = {
        ShowReportMethod.none: "show_none",
        ShowReportMethod.print_: "show_print",
        ShowReportMethod.curses: "show_curses",
    }

    # settings for this report
    settings: ReportSettings = Field(
        default_factory=ReportSettings, description="Settings for the report."
    )

    # selector for the report type. should be changed by subclasses to make
    # sure we select the correct model when deserializing
    report_type: Literal["basic"] = Field(
        "basic",
        description="Selector for the report type.",
        repr=False,
    )

    report_id: str = Field("root", description="ID for the report.")

    # status of the process that we report about.
    status: Status = Field(
        default=Status.RUNNING,
        description="Status of the underlying process.",
        repr=False,
    )

    if TYPE_CHECKING:
        __root__: BaseReport

    def __init__(
        self,
        *args,
        pulsar: Optional[PulsarMessageConsumer] = None,
        request: Optional[Dict] = None,
        response_properties: Optional[Dict] = None,
        submit: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._pulsar = pulsar
        self._request = request
        self._response_properties = response_properties
        if submit:
            self.submit()

    @classmethod
    def _combine_subclasses(cls, combined_type: Any) -> Any:
        """Recurse subclasses and combine them with a type."""
        for cls_ in cls.__subclasses__():
            combined_type = Union[combined_type, cls_]
            combined_type = cls_._combine_subclasses(combined_type)
        return combined_type

    @classmethod
    def from_payload(cls, payload: str) -> BaseReport:
        """Transform a payload to a report instance.

        This method takes into account all subclasses of the
        :class:`BaseReport` to find the correct one.
        """
        combined_type: Any = cls
        combined_type = cls._combine_subclasses(combined_type)
        Model: Type[BaseReport] = create_model(  # type: ignore
            "Report",
            __root__=(combined_type, Field(description="Report type")),
        )
        return Model.parse_raw(payload).__root__

    @classmethod
    def get_dummy_arguments(cls) -> Dict:
        """Get dummy argument to instantiate a report.

        This class method is supposed to generate arguments that can be used
        to create a report that shows nothing."""
        return {"settings": {"show_method": ShowReportMethod.none}}

    @classmethod
    def from_arg(cls, arg: Any) -> BaseReport:
        """Convenience method to generate a report from a generic argument.

        This method can be used to generate a report from a generic argument.
        It is supposed to be used as a quick function to generate a report that
        does nothing eventually.

        Parameters
        ----------
        arg: Any
            The argument that shall be interpreted as an input to generate a
            report.

            - If `arg` is an instance of this report class, it is returned
            - If `arg` is an instance of :class:`BaseReport`, this method
              returns a new report based using the `BaseReport` as an input
            - If `arg` is a dictionary, this is used to instantiate a new
              Report of this class
            - for any other argument, we return a silent report, i.e. one with
              :attr:`~deprogressapi.settings.ReportSettings.show_method` set
              to :attr:`deprogressapi.settings.none`.

        Examples
        --------

        This function takes an optional report argument and makes sure it has
        a report with the ``from_arg`` convenience function::

            from typing import Optional

            def reporting_function(report: Optional[BaseReport] = None):
                # now report may be None, using ``from_arg``, we make sure
                # that report is a real report class.
                report = BaseReport.from_arg(report)
        """
        if isinstance(arg, cls):
            ret = arg
        elif isinstance(arg, BaseReport) or isinstance(arg, dict):
            ret = cls.parse_obj(arg)
            ret._pulsar = getattr(arg, "pulsar", None)
            ret._request = getattr(arg, "request_msg", None)
        else:
            dummy_args = cls.get_dummy_arguments()
            ret = cls.parse_obj(dummy_args)
        return ret

    def submit(self) -> None:
        """Submit the report.

        This method submits the report and submits it via the pulsar or
        calls the :meth:`show` method."""
        if self.settings.show_method is None:
            return
        elif self._pulsar is not None:
            from demessaging.PulsarMessageConstants import (
                MessageType,
                PropertyKeys,
            )

            response_properties = self._response_properties or {}
            response_properties[PropertyKeys.STATUS] = self.status
            self._pulsar.send_response(
                request=self._request,
                msg_type=MessageType.PROGRESS,
                response_payload=self.json(),
                response_properties=response_properties,
            )
        else:
            self.show()

    def show(self) -> None:
        """Output the report.

        This uses the methods defined in the :attr:`show_methods` attribute
        based on the specified show method in the :attr:`settings`.
        """
        method_identifier = self.settings.get_show_method()
        method_name = self.show_methods[method_identifier]
        method: Callable[[], None] = getattr(self, method_name)
        return method()

    def show_print(self) -> None:
        """Show the report using pythons built-in :func:`print` function."""
        print(self.report_to_string())

    def show_curses(self) -> None:
        """Show the report using pythons built-in :func:`curses` module."""
        report = self.report_to_string()
        height, width = self.window.getmaxyx()
        lines = report.splitlines()[-height + 1 :]
        report = "\n".join([line[: width - 1] for line in lines])
        self.window.addstr(1, 0, report)
        self.window.clrtoeol()
        self.window.clearok(1)
        self.window.refresh()

    def show_none(self) -> None:
        """Dummy method that is called when the report_method is None"""
        pass

    @property
    def window(self) -> curses.window:  # type: ignore
        """A curses window for displaying the report.

        See Also
        --------
        show_curses
        """
        if self._window is None:
            self._window = curses.initscr()
        return self._window

    def report_to_string(self) -> str:
        """Render the report as a string."""
        return self.json(indent=2)

    def set_report_property(self, key: str, value):
        if self._response_properties is None:
            self._response_properties = {}

        self._response_properties[key] = value

    def complete(self, status: Status = Status.SUCCESS):
        """Mark the report as complete.

        This method marks the report as complete and closes eventually created
        widgets or curses windows.

        Parameters
        ----------
        status : Status, optional
            [description], by default Status.SUCCESS
        """
        self.status = status
        self.submit()
        if self._window is not None:
            curses.endwin()
            self._window = None
        if self._pulsar is not None:
            self._pulsar = None

    def __enter__(self):
        self.status = Status.RUNNING
        self.submit()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.complete(Status.SUCCESS if exc_value is None else Status.ERROR)

    def __repr_args__(self) -> ReprArgs:
        ret = dict(super().__repr_args__())
        ret.pop("status", None)
        ret.pop("report_type", None)
        ret.pop("settings", None)
        return list(ret.items())
