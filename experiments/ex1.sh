#!/bin/bash

echo "experiment:" > ex1.yaml
echo "  name: ex1.sh" >> ex1.yaml
echo "  date: '$(date +'%Y-%m-%d %H:%M:%S')'" >> ex1.yaml
echo >> ex1.yaml

PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 2 >> ex1.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 4 >> ex1.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 6 >> ex1.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex1.py -n 100 -b 2 -d 8 >> ex1.yaml
