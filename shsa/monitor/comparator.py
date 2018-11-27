"""Comparators.

"""

import numpy as np
import numbers


class Comparator(object):
    """Compares values against each other."""

    def compare(self, values):
        """Compares the values against each other.

        """
        raise NotImplementedError


class SimpleComparator(Comparator):
    def compare(self, values, error=1.0):
        """Simple comparison returning the number of mismatches.

        Returns the number of mismatches (given the allowed error) a value has
        with other values.

        """
        assert type(values) == list, "Parameter 'values' must be a list."
        # mismatch per value
        mismatch = [0]*len(values)
        with_idx = [set() for i in range(len(values))]
        # compare values against each other
        for i in range(len(values)):
            for j in range(i+1, len(values)):
                try:
                    if not np.isclose(values[i], values[j], atol=error):
                        mismatch[i] = mismatch[i] + 1
                        with_idx[i].add(j)
                        mismatch[j] = mismatch[j] + 1
                        with_idx[j].add(i)
                except TypeError:
                    # ignore values that are no numbers (e.g., None); do not
                    # count it as a mismatch (just like these values are not
                    # available)!
                    pass
        return mismatch, with_idx
