"""SHSA monitor.

__author__ = "Denise Ratasich"

Itoms are information distributed over the common network interface. Itoms are
linked to variables in the SHSA knowledge base (variable:itoms -- 1:*).

The monitor compares given itoms by transfering the itoms first into the common
domain. Relations probably have to be concatenated -> to substitutions.

"""

import networkx as nx
from collections import OrderedDict
import yaml

from monitor.monitor import Monitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel
from engine.dfs import DepthFirstSearch
from model.substitution import Substitution
from monitor.fault import FaultAgreement


class SHSAMonitor(Monitor):
    """SHSA Monitor notifies the search engine which observation failed given a
    SHSA model and a domain.

    """

    def __init__(self, model, domain, itoms=None, logfile=None):
        """Initialize the monitor.

        model -- SHSA knowledge base collecting the relations between
            variables.
        domain -- Common domain (a variable in the knowledge base) where the
            itoms will be compared to each other.
        itoms -- List of itoms (name only) which are inputs to monitor.
        logfile -- Path to a file where the monitor writes its logs to (yaml).
        """
        self.__model = model
        """SHSA knowledge base."""
        self.__domain = domain
        """Variable domain where the itoms shall be compared."""
        self.__itoms = itoms
        """List of itom (names) that will be monitored."""
        self.__logfile = logfile
        """Path to the log file."""
        if logfile is not None:
            self.__log_reset()  # init log variables
        self.__substitutions = None
        """Substitutions used to bring the itoms into the common domain."""
        if itoms is not None:
            self.__substitutions = self.__collect_substitutions(itoms)
        """Collect functions to transfer itoms to the domain (collect relations
        between itom/variable and domain)."""

    def __enter__(self):
        self.__log_reset()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__log_finish()

    @property
    def model(self):
        """Returns the underlying SHSA model."""
        return self.__model

    @property
    def domain(self):
        """Returns the monitoring domain."""
        return self.__domain

    @property
    def itoms(self):
        """Returns monitored itoms."""
        return self.__itoms

    @itoms.setter
    def itoms(self, itoms):
        """Sets the itoms to monitor."""
        self.__itoms = itoms
        # update used substitutions
        self.__substitutions = self.__collect_substitutions(itoms)

    @property
    def logfile(self):
        return self.__logfile

    def __log_reset(self):
        """Initializes or resets the log variables."""
        assert self.__logfile != None, "no need to init/reset log variables"
        # the logfile is opened in 'append' mode for logging, so
        # clean file before we start logging:
        with open(self.__logfile, 'w') as f:
            pass
        self.__log_timestamp = -1
        """Current time retrieved from the itoms (key: 't' or 'time') or a counter
        value (0, 1, ..)."""
        self.__log_data = []
        """Collects log data of monitor calls with equal timestamp."""

    def __log_finish(self):
        """Finishes log if necessary."""
        assert self.__logfile != None, "cannot finish a log without logfile"
        if len(self.__log_data) > 0:
            # write remaining log data (last timestamp)
            with open(self.__logfile, 'a') as f:
                if self.__log_timestamp > 0:
                    f.write("---\n")
                yaml.dump({'time': self.__log_timestamp,
                           'monitor_calls': self.__log_data}, f)

    def __log(self, itoms, istatus, out, ostatus):
        """Log data from the monitor to a yaml file.

        For each timestamp a yaml document is created (self.__log_data). The
        current document is appended to the logfile when a new bigger timestamp
        occurs.
        https://pyyaml.org/wiki/PyYAMLDocumentation

        The time is retrieved from the itoms. If not available a counter is
        used (0, 1, ...).

        Note, the given data is dumped when the timestamp changes
        (counter-mode: at next entrance).

        """
        assert self.__logfile != None, "cannot write log without logfile path"
        # retrieve timestamp from itoms
        timestamp = self.__log_timestamp + 1  # default counter
        if 'time' in itoms.keys():
            timestamp = float(itoms['time'])
        elif 't' in itoms.keys():
            timestamp = float(itoms['t'])
        # something to write and new timestamp?
        if len(self.__log_data) > 0 and timestamp > self.__log_timestamp:
            # dump logged data of the last timestamp
            with open(self.__logfile, 'a') as f:
                # signal new monitor call (start next yaml document)
                if self.__log_timestamp > 0:
                    f.write("---\n")
                yaml.dump({'time': self.__log_timestamp,
                           'monitor_calls': self.__log_data}, f)
                # reset yaml document fields
                self.__log_timestamp = timestamp
                self.__log_data = []
        # convert monitor call logs to python built-in types (avoid shsa
        # specific classes)
        subs = {'relations': [list(s.relations())
                              for s in self.__substitutions],
                'input_variables': [s.input_variables
                                    for s in self.__substitutions]}
        istatus_builtin = {key: int(value) for key, value in istatus.items()}
        itoms_builtin = {key: float(value) for key, value in itoms.items()}
        out_builtin = [float(v) if v is not None else None
                       for v in out.values()]
        ostatus_builtin = [int(value) for value in ostatus]
        data = {'itoms': itoms_builtin, 'istatus': istatus_builtin,
                'out': out_builtin, 'ostatus': ostatus_builtin,
                'substitutions': subs}
        # append
        self.__log_data.append(data)
        self.__log_timestamp = timestamp

    def __collect_substitutions(self, itoms):
        """Map itom to variable and find relations from variables to domain.

        Idea. Implement similar to substitute search (given itoms are
        provided). Find the shortest/best path from the variable represented by
        the itom to the domain. Search the variables like substitute search to
        find the broadest but flattest subtree where all variables are provided
        by the given itoms.

        -> Master Thesis of Thomas.

        Here: DFS all substitutions (itoms are provided variables).

        """
        # map itoms to variables
        provided_vars = [self.__model.variable(itom) for itom in itoms]
        # reset provided status of variables in the model; only the given itoms
        # are provided in the model (only substitutions with these itoms are
        # searched)
        for v in self.__model.variables:
            try:
                provided_status = True if v in provided_vars else False
                self.__model.set_property_to(v, 'provided', provided_status)
            except Exception:
                # we are not able to reset provided status of constants, this
                # is ok
                pass
        # get all possible substitutions
        search_engine = DepthFirstSearch(self.__model)
        substitutions = search_engine.substitute(self.__domain,
                                                 substitute_provided=False)
        # when the root is already provided an empty substitution is also valid
        if self.__model.provided([self.__domain]):
            s = Substitution(root=self.__domain, model=self.__model)
            substitutions.append(s)
        self.__substitutions = substitutions

    def monitor(self, itoms):
        """Analyze the given data for faults.

        itoms -- dictionary of itom names to value

        Returns the fault status per itom.

        """
        # recollect substitutions when itoms change
        if self.__itoms is None \
           or set(itoms.keys()) is not set(self.__itoms.keys()):
            self.__collect_substitutions(itoms)
        # get constants additionally to provisions
        constants = nx.get_node_attributes(self.__model, 'constant')
        # transfer the itoms into the common domain
        input_itoms = OrderedDict()
        out = OrderedDict()
        for i, s in enumerate(self.__substitutions):
            # transfer itoms to variables for the current substitution
            input_itoms[s] = []  # used itoms per substitution
            inputs = {}  # input (itom) values for execution of substitution
            for v in s.input_variables:
                if v in constants:
                    inputs[v] = self.__model.itoms(v)
                    continue
                # TODO: handle itoms for the same variable (how-to?) - here:
                # take first occurence
                for i in itoms:
                    if v == self.__model.variable(i):
                        input_itoms[s].append(i)
                        inputs[v] = itoms[i]
                        break
                if v not in inputs.keys():
                    raise RuntimeError("""No corresponding itom found for
                    variable {}.""".format(v))
            # bring to common domain
            out[s] = s.execute(inputs)
        # agree about the fault status of the output values
        a = FaultAgreement()
        vstatus = a.agree(list(out.values()), error=0.1)
        # map value status to itom status
        # note that it is unclear which of the inputs caused the fault -> all
        # are marked faulty!
        istatus = {i: ItomFaultStatusType.OK for i in itoms}
        for i, s in enumerate(self.__substitutions):
            for itom in input_itoms[s]:
                istatus[itom] = vstatus[i]
        # log if desired
        if self.__logfile is not None:
            self.__log(itoms, istatus, out, vstatus)
        return istatus
