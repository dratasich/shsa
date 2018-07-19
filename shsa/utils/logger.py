"""YAML logger.

__date__ = 2018-07-09
__author__ = "Denise Ratasich"

Means to read, write and append to a YAML log file.

See also https://pyyaml.org/wiki/PyYAMLDocumentation.

"""

import yaml
import math


class Logger(object):
    """Logs data to a file in YAML format."""

    def __init__(self, logfile, mode='r'):
        """Initialize the logger.

        logfile -- Path to a file where the logs should be written to (yaml).

        """
        self.__logfile = logfile
        """Path to the log file."""
        self.__documents = None
        """Data from a YAML log file, as list of YAML documents. Read mode
        only."""
        self.__timestamp = 0
        """Current time retrieved from the data to log (key: 't' or 'time') or
        a counter value (0, 1, ..)."""
        self.__mode = mode
        """Read 'r', write 'w' or append 'a' mode."""
        if mode == 'r':
            self.__read()  # read all data to self.__documents
        elif mode == 'w':
            self.__reset()  # clean log file / delete file contents
        elif mode == 'a':
            self.__read()  # just to specify a next timestamp
            # next timestamp assuming that the file has ascending time
            self.__timestamp = int(self.__documents[-1]['time']) + 1
            self.__documents = None
        else:
            raise RuntimeError("Unknown mode. Only 'r', 'w', and 'a' allowed.")

    @property
    def logfile(self):
        return self.__logfile

    @property
    def documents(self):
        return self.__documents

    def __reset(self):
        """Resets variables and deletes the contents of a logfile."""
        # clean file before we start logging
        with open(self.__logfile, 'w') as f:
            pass
        # reset counter
        self.__timestamp = 0

    def __read(self):
        """Read a log file."""
        self.__documents = []
        with open(self.__logfile, 'r') as f:
            for data in yaml.load_all(f):
                self.__documents.append(data)
        # reset counter
        self.__timestamp = 0

    def log(self, **kwargs):
        """Logs the given keyword arguments.

        Specify timestamps via the keyword 'time', e.g. "time=0.1".

        Note that the arguments should contain built-in types only to get a
        readable yaml file. Otherwise the classes and binaries will be logged
        to the file.

        """
        if self.__mode not in {'w', 'a'}:
            raise RuntimeError("log is only allowed in write and append mode")
        """Log data from keyworded, variable-length dictionary **kwargs."""
        assert self.__logfile is not None, \
            "cannot write log without logfile path"
        # default counter (when kwarg does not contain 'time' key)
        timestamp = self.__timestamp + 1
        # prepare YAML document to dump
        document = {'time': timestamp}
        document.update(kwargs)  # may override 'time'
        # dump logged data of the last timestamp
        with open(self.__logfile, 'a') as f:
            f.write("---\n")
            yaml.dump(document, f)

    def get(self, time=None, tolerance=0.1):
        """Returns the next document from the log file,
        or a list of documents when time is given.

        time -- Timestamp.
        tolerance -- Absolute tolerance for the time value.

        """
        if self.__mode != 'r':
            raise RuntimeError("get is only allowed in read mode")
        if time is None:
            # simply get the next document
            self.__timestamp = int(self.__timestamp) + 1
            assert self.__timestamp > 0
            if self.__timestamp < len(self.__documents):
                return self.__documents[self.__timestamp]
        else:
            # return a list of documents with the same timestamp
            return list(filter(lambda document:
                               math.isclose(document['time'], time,
                                            abs_tol=tolerance),
                               self.__documents))
        return None
