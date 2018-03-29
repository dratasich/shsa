"""SHSA monitor.

__author__ = "Denise Ratasich"

Itoms are information distributed over the common network interface. Itoms are
linked to variables in the SHSA knowledge base (variable:itoms -- 1:*).

The monitor compares given itoms by transfering the itoms first into the common
domain. Relations probably have to be concatenated. A relation has the same
structure as given in the YAML config file. However, instead of variables, the
mapped itoms are added, e.g., {'in': [(var_1, itom_1), (var_2, itom_2)], 'fct':
"f1"}.

"""

from monitor.monitor import Monitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel


class SHSAMonitor(Monitor):
    """SHSA Monitor notifies the search engine which observation failed given a
    SHSA model and a domain.

    """

    def __init__(self, model, domain):
        """Initialize the monitor.

        model -- SHSA knowledge base collecting the relations between
            variables.
        domain -- Common domain (a variable in the knowledge base) where the
            itoms will be compared to each other.
        """
        self.__model = model
        """SHSA knowledge base."""
        self.__domain = domain
        """Variable domain where the itoms shall be compared."""
        self.__relations = None
        """Collect functions to transfer itoms to the domain (collect relations
        between itom/variable and domain)."""

    def __get_model(self):
        """Returns the underlying SHSA model."""
        return self.__model

    model = property(__get_model)

    def __get_domain(self):
        """Returns the monitoring domain."""
        return self.__domain

    domain = property(__get_domain)

    def __get_relations(self, itoms):
        """Map itom to variable and find relations from variables to domain.

        Idea. Implement similar to substitute search (given itoms are
        provided). Find the shortest/best path from the variable represented by
        the itom to the domain. Search the variables like substitute search to
        find the broadest but flattest subtree where all variables are provided
        by the given itoms.

        -> Master Thesis of Thomas.

        Here we just hard-code it per model and domain.

        """
        # collect relations such that as many as possible itoms are used
        # for now: hard code the relations here (itoms -> variables -> fct ->
        # domain)
        if self.__domain == 's':
            self.__relations = {}
            r12 = {'in': [('m', 'i_m'), ('p', 'i_p')],
                   'fct': "m"}
            self.__relations['r12'] = r12
            r3 = {'in': [('n', 'i_n'), ('t', 'i_t')], 'fct': "n"}
            self.__relations['r3'] = r3
            r6 = {'in': [('s', 'i_s'), ('t', 'i_t')],
                  'fct': "s"}
            self.__relations['r6'] = r6
            r7 = {'in': [('n', 'i_n')],
                  'fct': "n if True else 1"}
            self.__relations['r7'] = r7
        # The relations are chosen such that only the given/provided itoms are
        # used. The itoms hold the values (not the variables) so instead of
        # writing the variables as inputs, e.g.,
        # r12 = {'in': ['m', 'p'], 'fct': "m"}
        # we add the itoms to the inputs:
        # r12 = {'in': [('m', 'i_m'), ('p', 'i_p')], 'fct': "m"}
        return self.__relations

    def __execute_relation(self, r, itoms):
        """Code-generates the given relation, executes it and returns the
        output of the relation.

        r -- Relation, a dictionary of structure {in: [], fct: ""}.
        itoms -- Information sources, contain the inputs for the relation.

        """
        VAR_IDX = 0
        ITOM_IDX = 1
        # inputs of the relation
        parameters = ", ".join([var for var, itom in r['in']])
        # initial code string
        code = "\n"
        # define relation as Python function
        code += "def f(" + parameters + "):\n"
        code += "    return (" + r['fct'] + ")\n"
        code += "\n"
        # get value from itoms for each input variable of the relation
        if not {i[ITOM_IDX] for i in r['in']}.issubset(set(itoms)):
            raise RuntimeError("""Missing input itoms for relation:
            {}.""".format(set(r['in']).difference(set(itoms))))
        for var, itom in r['in']:
            # create assignment of var = itom_value
            code += str(var) + " = " + str(itoms[itom]) + "\n"
        # call relation
        code += "out = f(" + parameters + ")\n"
        # create local variables for the code
        local_vars = {'out': None}
        # execute the code
        exec(code, None, local_vars)
        return local_vars['out']

    def __transfer(self, itoms, relations):
        """Transfers itoms into the common domain using the relations.

        itoms -- inputs for all relations
        relations -- functions to derive selected inputs to the domain

        Returns the list of relations, appended with the derived output value.

        Output format (example): [{'in': [..], 'fct': "..", 'out': value_1},
        {'in': [..], 'fct': "..", 'out': value_2}, ..].

        """
        for r in relations.values():
            r['out'] = self.__execute_relation(r, itoms)
        return relations

    def __compare(self, itoms, relations, error):
        """Simple comparison given a maximal allowed error.

        Considers Byzantine faults (no assumptions on failure modes, e.g.,
        fail-stop), e.g., advertising a wrong value. To be resilient to every
        possible action that can occur.

        """
        # initial fault status of itoms
        status = {i: ItomFaultStatusType.OK for i in itoms}
        # compare values against each other
        mismatch = {r: 0 for r in relations}  # mismatch per relation
        for r1 in relations:
            for r2 in relations:
                if r1 == r2:
                    continue
                if abs(relations[r1]['out'] - relations[r2]['out']) >= error:
                    mismatch[r1] = mismatch[r1] + 1
        # map faulty relation output to inputs (note that it is unclear which
        # of the inputs caused the fault -> all are marked faulty!)
        for r in relations:
            if mismatch[r] >= 2:  # set a suitable value
                for _, itom in relations[r]['in']:
                    status[itom] = ItomFaultStatusType.FAULTY
        return status

    def monitor(self, itoms):
        """Analyze the given data for faults.

        Returns the fault status of the itoms.

        """
        # transfer the itoms into the common domain
        relations = self.__get_relations(itoms)
        relations = self.__transfer(itoms, relations)  # output value appended
        # analyze
        return self.__compare(itoms=itoms, relations=relations, error=0.1)
