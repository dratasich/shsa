"""Comparators.

"""

import math


class Comparator(object):
    """Compares values against each other."""

    def compare(self, values):
        """Compares the values against each other.

        """
        raise NotImplementedError


class SimpleComparator(Comparator):
    def compare(self, values, error=1.0):
        """Simple comparison given a maximal allowed error.

        Considers Byzantine faults (no assumptions on failure modes, e.g.,
        fail-stop), e.g., advertising a wrong value. To be resilient to every
        possible action that can occur.

        Returns the number of mismatches (given the allowed error) a value has
        with other values.

        """
        assert type(values) == list, "Parameter 'values' must be a list."
        # mismatch per value
        mismatch = [0]*len(values)
        # compare values against each other
        for i in range(len(values)):
            for j in range(i+1, len(values)):
                if not math.isclose(values[i], values[j], abs_tol=error):
                    mismatch[i] = mismatch[i] + 1
                    mismatch[j] = mismatch[j] + 1
        return mismatch
