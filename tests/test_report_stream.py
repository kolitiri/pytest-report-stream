# -*- coding: utf-8 -*-

def test_report_streaming_for_sync_test(pytester):
    """ Asserts that the plugin works for synchronous tests
    and it live streams report events in each test run.
    """
    pytester.makeconftest("""
        import asyncio

        import pytest


        @pytest.fixture(scope="session")
        def event_loop():
            # Use `get_event_loop_policy` to create a new loop and to
            # avoid deprecation warnings of `get_event_loop` in v3.10.
            # `get_event_loop_policy` might still be deprecated in v3.12
            policy = asyncio.get_event_loop_policy()
            loop = policy.new_event_loop()
            yield loop
            loop.close()
    """)

    pytester.makepyfile("""
        def test_sync():
            pass
    """)

    result = pytester.runpytest(
        '--stream-reports',
        '-vvvs',
    )

    # Assert we logged out 3 report events:
    # 1. One in the begining of the test-run,
    # 2. One for the `test_sync` test
    # 3. One in the end of the test-run
    result.stdout.fnmatch_lines([
        "*'summary': {'passed': 0, 'failed': 0, 'status': 'in-progress'}*",
        "*'summary': {'passed': 1, 'failed': 0, 'status': 'in-progress'}*",
        "*'summary': {'passed': 1, 'failed': 0, 'status': 'passed'}*",
    ])

    # Assert we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_report_streaming_for_async_test(pytester):
    """ Asserts that the plugin works for asynchronous tests
    and it live streams report events in each test run.
    """
    pytester.makeconftest("""
        import asyncio

        import pytest


        @pytest.fixture(scope="session")
        def event_loop():
            # Use `get_event_loop_policy` to create a new loop and to
            # avoid deprecation warnings of `get_event_loop` in v3.10.
            # `get_event_loop_policy` might still be deprecated in v3.12
            policy = asyncio.get_event_loop_policy()
            loop = policy.new_event_loop()
            yield loop
            loop.close()
    """)

    pytester.makepyfile("""
        import pytest

        @pytest.mark.asyncio
        async def test_async():
            pass
    """)

    result = pytester.runpytest(
        '--stream-reports',
        '-vvvs',
    )

    # Assert we logged out 3 report events:
    # 1. One in the begining of the test-run,
    # 2. One for the `test_async` test
    # 3. One in the end of the test-run
    result.stdout.fnmatch_lines([
        "*'summary': {'passed': 0, 'failed': 0, 'status': 'in-progress'}*",
        "*'summary': {'passed': 1, 'failed': 0, 'status': 'in-progress'}*",
        "*'summary': {'passed': 1, 'failed': 0, 'status': 'passed'}*",
    ])

    # Assert we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_report_streaming_with_custom_client(pytester):
    """Asserts the `DefaultReportClient` was successfully overriden
    by the `myCustomReportClient` in the user's `pytest_configure`.
    """
    pytester.makeconftest("""
        import asyncio

        import pytest
        from pytest_report_stream import ReportClient, ReportStreamPlugin


        class myCustomReportClient(ReportClient):
            async def publish_report(self, report_msg: dict) -> None:
                print('Some log comming from my custom report client')


        @pytest.fixture(scope="session")
        def event_loop():
            # Use `get_event_loop_policy` to create a new loop and to
            # avoid deprecation warnings of `get_event_loop` in v3.10.
            # `get_event_loop_policy` might still be deprecated in v3.12
            policy = asyncio.get_event_loop_policy()
            loop = policy.new_event_loop()
            yield loop
            loop.close()


        def pytest_configure(config):
            if config.option.stream_reports:
                config._stream_reports = ReportStreamPlugin(
                    report_client=myCustomReportClient()
                )
                config.pluginmanager.register(config._stream_reports)
    """)

    pytester.makepyfile("""
        import pytest

        @pytest.mark.asyncio
        async def test_async():
            pass
    """)

    result = pytester.runpytest(
        '--stream-reports',
        '-vvvs',
    )

    result.stdout.fnmatch_lines([
        "*Some log comming from my custom report client*",
    ])

    # Assert we get a '0' exit code for the testsuite
    assert result.ret == 0
