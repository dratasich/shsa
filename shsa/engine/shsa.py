"""Interface for search engines for Self-Healing by Structural Adaptation
(SHSA).

"""

from model.shsamodel import SHSAModel


class SHSA(object):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, model=None, graph=None, properties=None,
                 configfile=None):
        """Initializes the engine with a model."""
        if model is not None:
            self.__model = model
            """Knowledge base for SHSA."""
        else:
            self.__model = SHSAModel(graph, properties, configfile)

    def __get_model(self):
        """Returns the underlying SHSA model."""
        return self.__model

    model = property(__get_model)

    def substitute(self, root):
        raise NotImplementedError
