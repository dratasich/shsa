#!/bin/bash
# profilehooks has been adapted to create this type of output!
# line 780 of profilehooks.py (csv like output):
# print("%s,"
#       "%d,%.6f" % (
#           funcname, self.ncalls,
#           self.totaltime)
#       )

echo "%branch, model, shsa, shsa_n, shsa_et, orr, orr_n, orr_et" > ex3.csv


n=10  # number of ex2.py runs per model
m=100  # different models (only one is generated for a ex2.py run)
a=0.2
d=6  # constant depth
branches="1 2 3 4"  # different branching factor

for b in $branches
do
    # run experiments with m different models
    for i in $(seq "$m")
    do
        # run experiment n times (one model)
        params="-n $n -b $b -d $d -a $a rss_once orr"
        res=$(PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex3.py $params | grep -A 2 "measurements" | tail -n 2)
        echo "$b,$i,"$res | sed -e "s/ /,/g" >> ex3.csv
    done
done
