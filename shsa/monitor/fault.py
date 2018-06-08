"""Fault types.

"""

from enum import IntEnum

from monitor.comparator import SimpleComparator


class ItomFaultStatusType(IntEnum):
    """Types of fault status considered."""
    OK = 0
    """Check with other redundant information was ok."""
    UNDEFINED = 1
    """We cannot make a point about the status of the information itom.

    For example:
    - There is no related information to check against.
    - It is unclear which itom is faulty (2-itom-comparison).

    """
    FAULTY = 2
    """Check with at least two other redundant sources failed
    (>3-itom-comparison).

    """


class FaultAgreement(object):
    """Agrees about the fault status of a given list of values that should
    match.

    """

    def agree(self, values, error=1.0):
        """Annotate the values with a fault status."""
        assert type(values) == list, "Parameter 'values' must be a list."
        # compare
        c = SimpleComparator()
        mismatches, with_idx = c.compare(values, error=error)
        # 1-fault-tolerant
        faulty_idx = set()
        for i, m in enumerate(mismatches):
            if m > 1:  # at least two other values mismatch
                faulty_idx.add(i)
        if len(faulty_idx) > 1:
            # more than one value incorrect, inconsistent
            return [ItomFaultStatusType.UNDEFINED]*len(values)
        if len(faulty_idx) == 0 and sum(mismatches) > 0:
            # too few redundancies to judge fault
            return [ItomFaultStatusType.UNDEFINED]*len(values)
        # set status
        status = [ItomFaultStatusType.OK]*len(values)
        for i, v in enumerate(values):
            if mismatches[i] > 1:
                status[i] = ItomFaultStatusType.FAULTY
            # handle no numbers due to unsatisfied constraints
            if v is None:
                # constraint wasn't satisfied for substitution s, we cannot
                # judge the inputs of s
                status[i] = ItomFaultStatusType.UNDEFINED
        return status
