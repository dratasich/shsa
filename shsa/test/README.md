# Test

Execute (unit-)tests in `..` by:

```bash
$ python3 -m unittest discover
```

Debug a failed testcase:

```bash
$ PYTHONPATH=./ pdb3 test/test_model.py
```

From emacs:
* `M-:` and evaluate `setenv "PYTHONPATH" "./"`
* Invoke `M-x pdb`
* Run `pdb` like: `python3 -m pdb test/test_substitution.py`

[Profile](http://www.scipy-lectures.org/advanced/optimizing/) an engine
with [cProfile](https://docs.python.org/3/library/profile.html):

```bash
$ python3 -m cProfile -o uc_shsa.prof uc_shsa.py -g
$ ../scripts/profile_stats.py uc_shsa.prof | grep shsa
```
