#!/bin/bash

echo "ex1.sh\n" > ex1.yaml

PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 2 >> ex1.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 4 >> ex1.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 6 >> ex1.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 8 >> ex1.yaml
