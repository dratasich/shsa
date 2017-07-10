# shsa
Self-Healing by Structural Adaptation


## Algorithms

* substitution


## Dependencies

* [networkx](https://networkx.readthedocs.io/en/stable/install.html) is used
  for the underlying graph model.
* [PyYAML](http://pyyaml.org/wiki/PyYAMLDocumentation) to import a model from a
  yaml-file.
* [graphviz](http://www.graphviz.org/) `dot` to plot a model.


## Tests

Execute (unit-)tests in `./shsa/` by:

```bash
python -m unittest discover
```

## Docs

### Plots

The graphs can be exported to dot files and further to image formats (e.g., png
or pdf). To integrate a dot-file into a Latex document, one may use
[dot2texi](http://www.ctan.org/pkg/dot2texi).
