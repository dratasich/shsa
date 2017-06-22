"""Interface for search engines for Self-Healing by Structural Adaptation
(SHSA).

"""

from model.shsamodel import SHSAModel, SHSANodeType

class SHSA(object):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the engine with a model."""
        self._model = SHSAModel(graph, properties, configfile)
        """Knowledge base for SHSA."""

    def __get_model(self):
        """Returns the underlying SHSA model."""
        return self._model

    model = property(__get_model)

    def substitute(self, root):
        raise NotImplementedError
