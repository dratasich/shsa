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
python3 -m unittest discover
```

Debug a failed testcase:

```bash
pdb3 test/test_model.py
```

From emacs:
* Invoke `M-x pdb`
* Run `pdb` like: `python3 -m pdb test/test_substitution.py`


## Docs

### Plots

The graphs can be exported to dot files and further to image formats (e.g., png
or pdf). To integrate a dot-file into a Latex document, one may use
[dot2texi](http://www.ctan.org/pkg/dot2texi).
