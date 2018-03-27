"""Interface for monitors.

"""


class Monitor(object):
    """Monitor notifies the search engine which observation failed."""

    def __init__(self, itom):
        """Initialize the monitor."""

    def monitor(self, itoms):
        """Analyze the given data for faults.

        Returns the fault status of the itoms.

        """
        raise NotImplementedError
