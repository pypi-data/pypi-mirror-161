"""Print report to generate output."""
from __future__ import annotations

from typing import List

from deprogressapi.base import BaseReport, Status
from pydantic import Field

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal  # type: ignore


class PrintReport(BaseReport):
    """A simple report to print a statement."""

    report_type: Literal["print"] = Field(  # type: ignore
        "print", description="Selector for the report type."
    )

    messages: List[str] = Field(
        default_factory=list, description="The message to print."
    )

    def report_to_string(self) -> str:
        return "\n".join(self.messages).rstrip()

    def show_print(self) -> None:
        """Only print the last message."""
        print(self.messages[-1])

    def show(self) -> None:
        """Reimplement to only show the report when it's complete."""
        if self.messages:
            if self.status != Status.SUCCESS or self.messages[-1]:
                return super().show()

    def print(self, message: str) -> None:
        """Update the report and show the message."""
        self.messages.append(message)
        self.status = Status.RUNNING
        self.submit()

    def error(self, message: str) -> None:
        """Display an error message."""
        self.messages.append(message)
        self.status = Status.ERROR
        self.submit()

    def complete(
        self, status: Status = Status.SUCCESS, message: str = ""
    ) -> None:
        """Mark the report as complete.

        This method marks the report as complete and closes eventually created
        widgets or curses windows. You can submit an additional message that
        will then be added to the report.

        Parameters
        ----------
        status : Status, optional
            [description], by default Status.SUCCESS
        """
        self.messages.append(message)
        return super().complete(status=status)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_value is not None:
            self.messages.append(str(exc_value))
        return super().__exit__(exc_type, exc_value, exc_tb)
