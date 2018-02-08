# shsa

This is the Python library of shsa.

## Scripts

`uc_shsa.py` substitutes a variable of a knowledge base encoded in yaml with
the given algorithm.

Example:
```bash
$ ./uc_shsa.py -r steering_angle -c ../config/drivetrain.yaml --shpgsa
```

The knowledge base and substitution is printed for convinience (dot, pdf).
