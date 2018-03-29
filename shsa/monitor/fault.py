"""Fault types.

"""

from enum import IntEnum


class ItomFaultStatusType(IntEnum):
    """Types of fault status considered."""
    OK = 0
    FAULTY = 1
