from enum import Enum


TestStatus = Enum(
    "TestStatus",
    """
    erred
    failed
    passed
    running
    skipped
    """)
