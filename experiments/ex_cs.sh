#!/bin/bash

echo "experiment:" > ex_cs.yaml
echo "  name: ex_cs.sh" >> ex_cs.yaml
echo "  date: '$(date +'%Y-%m-%d %H:%M:%S')'" >> ex_cs.yaml
echo >> ex_cs.yaml

n=100

PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex_cs.py -n $n dmin ../../ros/shsa-pkg/config/rover.yaml >> ex_cs.yaml
PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex_cs.py -n $n steering_angle ../config/drivetrain.yaml >> ex_cs.yaml
