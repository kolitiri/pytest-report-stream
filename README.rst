.. -*- mode: rst; coding: utf-8 -*-

============================================================
pytest-report-stream - Live stream test reports
============================================================

.. image:: https://img.shields.io/pypi/v/pytest-report-stream.svg
    :target: https://pypi.org/project/pytest-report-stream
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-report-stream.svg
    :target: https://pypi.org/project/pytest-report-stream
    :alt: Python versions


:Authors: Christos Liontos
:Version: 0.1.0
:Date:    2023-09-22
:Download: https://pypi.python.org/pypi/pytest-report-stream#downloads
:Code: https://github.com/kolitiri/pytest-report-stream


Welcome to pytest-report-stream!
============================================================
pytest-report-stream is a pytest plugin which allows to stream test reports at runtime.

It is a simple plugin the leverages pytest's build-in hook `pytest_runtest_makereport <https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_runtest_makereport>`_ to intercept test execution and publish the status of the test run.

The plugin produces report events at specific moments:
- One report in the beginning of the test run
- One report in the end of each test
- One report in the end of the test run

The report structure looks like the dictionary below:

.. code-block:: python3

    {
        "test_run_tag": "My first test framework",
        "test_run_id": "5e080accaee748dc80619ee99245124e",
        "timestamps": {
            "started": datetime.datetime(2023, 10, 22, 17, 4, 43, 161646),
            "duration": 0.002042,
            "finished": datetime.datetime(2023, 10, 22, 17, 4, 43, 163688),
        },
        "summary": {"passed": 1, "failed": 1, "status": "in-progress"},
        "results": {
            "tests/test_module1": {
                "test_func_1": {
                    "name": "test_func_1",
                    "description": "Docstrings of function 1",
                    "status": "passed",
                    "error": "None",
                },
                "test_func_2": {
                    "name": "test_func_2",
                    "description": "Docstrings of function 2",
                    "status": "failed",
                    "error": "None",
                }
            }
        },
    }

Use cases
------------------------------------------------------------
The ``pytest-report-stream`` plugin can be particularly useful while running large and long lasting integration testing suites using pytest.

The plugin can be used to stream live report events to a remote service, allowing to monitor the progress and the status of the tests.

For example, Jenkins and other CI/CD tools are great, but there might be a requirement to aggregate test results from multiple builds.


Installation
============================================================
Install the plugin as below.

.. code-block:: sh

    pip install pytest-report-stream


Usage
============================================================
The plugin is available after installation and can be enabled using the ``--stream-reports`` flag.

.. code-block:: sh

    pytest --stream-reports

The plugin is using a ``report_client: ReportClient`` instance to generate the reports.

A default report_client is used to log the reports in STDOUT. (Note that in order to view the reports in STDOUT you will need to run ``pytest`` with the flag ``-s``)

The default client can be overriden in your own ``pytest_configure`` with an implementation of the abstract ``pytest_report_stream::ReportClient`` class.

Synchronous test using the default STDOUT report client
------------------------------------------------------------

.. code-block:: python3

    # content of tests/test_my_module.py
    def test_sync():
        pass

Aynchronous test using the default STDOUT report client
------------------------------------------------------------

.. code-block:: python3

    # content of tests/test_my_module.py
    import pytest

    @pytest.mark.asyncio
    async def test_async():
        pass

Aynchronous test using a custom report client
------------------------------------------------------------

.. code-block:: python3

    # content of tests/conftest.py
    import pytest
    from pytest_report_stream import ReportClient, ReportStreamPlugin


    class myCustomReportClient(ReportClient):
        async def publish_report(self, report_msg: dict) -> None:
            print('Some log comming from my custom report client')


    def pytest_configure(config):
        if config.option.stream_reports:
            config._stream_reports = ReportStreamPlugin(
                report_client=myCustomReportClient()
            )
            config.pluginmanager.register(config._stream_reports)

.. code-block:: python3

    # content of tests/test_my_module.py
    import pytest

    @pytest.mark.asyncio
    async def test_async():
        pass

You can implement the ``publish_report`` function and do pretty much anything, such as publishing the events to a message broker.


Requirements
============================================================
* pytest>=7.0.0
* pytest-asyncio


Contributing
============================================================
Contributions are very welcome.

Tests can be run with `tox <https://tox.wiki/en>`_, please ensure
the coverage at least stays the same before you submit a pull request.

.. code-block:: sh

    tox


License
============================================================
Distributed under the terms of the MIT license, "pytest-report-stream" is free and open source software


Issues
============================================================
If you encounter any problems, please `file an issue <https://github.com/kolitiri/pytest-report-stream/issues>`_ along with a detailed description.
