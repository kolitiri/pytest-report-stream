# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generator,
    Optional,
)
import uuid

import pytest
import pytest_asyncio


PHASE_REPORT_KEY: pytest.StashKey = (
    pytest.StashKey[Dict[str, pytest.CollectReport]]()
)


class Status(Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    IN_PROGRESS = 'in-progress'
    CANCELLED = 'cancelled'
    SKIPPED = 'skipped'


class ReportClient(ABC):
    @abstractmethod
    async def publish_report(self, report_msg: dict) -> None:
        ...


class DefaultReportClient(ReportClient):
    async def publish_report(self, report_msg: dict) -> None:
        print(report_msg)


class ReportStreamPlugin:
    """Pytest plugin class uset to stream test reports at runtime"""
    def __init__(
        self,
        report_client: ReportClient = None,
        test_run_tag: Optional[str] = None,
        test_run_id: Optional[str] = None,
    ) -> None:
        self.report_client = report_client or DefaultReportClient()
        self.test_run_tag = test_run_tag or ''
        self.test_run_id = test_run_id or uuid.uuid4().hex

        self.session_timestamps = {}
        self.session_summary = {}
        self.session_results = {}

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(
        self,
        item: Callable,
        call,
    ) -> Generator[None, Any, None]:
        """Pytest hook that wraps the standard pytest_runtest_makereport
        function and grabs the results for the 'call' phase of each test.
        """
        outcome = yield
        report = outcome.get_result()

        test_cls_docstring = item.parent.obj.__doc__ or ''
        test_fn_docstring = item.obj.__doc__ or ''
        report.description = test_fn_docstring or test_cls_docstring

        report.exception = None
        if report.outcome == "failed":
            exception = call.excinfo.value
            report.exception = exception

        item.stash.setdefault(PHASE_REPORT_KEY, {})[report.when] = report

    @pytest_asyncio.fixture(scope="session", autouse=True)
    async def first_last_report(
        self,
        request,
    ) -> AsyncIterator[None]:
        """Pytest fixture that publishes the first and last report"""
        started = datetime.now()

        self.session_timestamps["started"] = started
        self.session_summary["passed"] = 0
        self.session_summary["failed"] = 0
        self.session_summary["status"] = Status.IN_PROGRESS.value

        # Send the initial report message
        await self.report_client.publish_report(
            dict(
                test_run_tag=self.test_run_tag,
                test_run_id=self.test_run_id,
                timestamps=self.session_timestamps,
                summary=self.session_summary,
                results=self.session_results,
            )
        )

        # Wait until all the tests are completed
        yield

        total_tests = request.session.testscollected
        failed_tests = request.session.testsfailed
        passed_tests = total_tests - failed_tests

        finished = datetime.now()
        duration = (finished - started).total_seconds()

        self.session_timestamps["finished"] = finished
        self.session_timestamps["duration"] = duration
        self.session_summary["passed"] = passed_tests
        self.session_summary["failed"] = failed_tests
        self.session_summary["status"] = (
            Status.FAILED.value
            if request.session.testsfailed
            else Status.PASSED.value
        )

        # Send a final report message
        await self.report_client.publish_report(
            dict(
                test_run_tag=self.test_run_tag,
                test_run_id=self.test_run_id,
                timestamps=self.session_timestamps,
                summary=self.session_summary,
                results=self.session_results,
            )
        )

    @pytest_asyncio.fixture(autouse=True)
    async def report(
        self,
        request,
    ) -> AsyncIterator[None]:
        """Pytest fixture that publishes a report every
        time an individual unit test has been completed.
        """

        # Wait until the test is completed
        yield

        # Gather test results
        report = request.node.stash[PHASE_REPORT_KEY]

        test_module = report["call"].fspath.split(".")[0]
        test_name = report["call"].head_line.replace(".", "::")
        test_description = report["call"].description
        passed = report["call"].passed
        failed = report["call"].failed
        skipped = report["call"].skipped
        exception = repr(report["call"].exception)

        status = None
        if passed:
            status = Status.PASSED.value
            self.session_summary["passed"] += 1
        elif failed:
            status = Status.FAILED.value
            self.session_summary["failed"] += 1
        elif skipped:
            status = Status.SKIPPED.value

        started = self.session_timestamps["started"]
        self.session_timestamps["duration"] = (
            (datetime.now() - started).total_seconds()
        )

        self.session_results.setdefault(test_module, {})[test_name] = dict(
            name=test_name,
            description=test_description,
            status=status,
            error=exception,
        )

        # Send a report message including the new test
        await self.report_client.publish_report(
            dict(
                test_run_tag=self.test_run_tag,
                test_run_id=self.test_run_id,
                timestamps=self.session_timestamps,
                summary=self.session_summary,
                results=self.session_results,
            )
        )


def pytest_addoption(parser):
    group = parser.getgroup('report-stream')
    group.addoption(
        '--stream-reports',
        dest='stream_reports',
        action='store_true',
        help='Enable report streaming'
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """If report streaming is enabled, use the default report client.
    The client can be overridden in the user's pytest_configure call.
    """
    if config.option.stream_reports:
        config._stream_reports = ReportStreamPlugin()
        config.pluginmanager.register(config._stream_reports)
