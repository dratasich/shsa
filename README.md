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
PYTHONPATH=./ pdb3 test/test_model.py
```

From emacs:
* `M-:` and evaluate `setenv "PYTHONPATH" "./"`
* Invoke `M-x pdb`
* Run `pdb` like: `python3 -m pdb test/test_substitution.py`

[Profile](http://www.scipy-lectures.org/advanced/optimizing/) an engine
with [cProfile](https://docs.python.org/3/library/profile.html):

```bash
python3 -m cProfile -o uc_shsa.prof uc_shsa.py -g
../scripts/profile_stats.py uc_shsa.prof | grep shsa
```


## Docs

### Plots

The graphs can be exported to dot files and further to image formats (e.g., png
or pdf). To integrate a dot-file into a Latex document, one may
use [dot2texi](http://www.ctan.org/pkg/dot2texi).
