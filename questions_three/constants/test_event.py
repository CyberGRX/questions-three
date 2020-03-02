from enum import Enum


TestEvent = Enum(
    "TestEvent",
    """
    artifact_created
    http_request_sent
    http_response_received
    report_created
    sample_measured
    suite_ended
    suite_erred
    suite_results_compiled
    suite_started
    test_ended
    test_failed
    test_erred
    test_skipped
    test_started
    """)
