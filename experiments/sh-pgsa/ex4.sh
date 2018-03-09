#!/bin/bash
# profilehooks has been adapted to create this type of output!
# line 780 of profilehooks.py (csv like output):
# print("%s,"
#       "%d,%.6f" % (
#           funcname, self.ncalls,
#           self.totaltime)
#       )

echo "%branch, model, shsa, shsa_n, shsa_et, orr, orr_n, orr_et" > ex4.csv


n=10  # number of ex4.py runs per model
m=100  # different models (only one is generated for a ex4.py run)
a=0.2
d=8  # constant depth
branches="1 2 3 4 5 6"  # different branching factor

for b in $branches
do
    # run experiments with m different models
    for i in $(seq "$m")
    do
        # run experiment n times (one model)
        params="-n $n -b $b -d $d -a $a rss_once orr"
        res=$(PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex4.py $params | grep -A 2 "measurements" | tail -n 2)
        echo "$b,$i,"$res | sed -e "s/ /,/g" >> ex4.csv
    done
done
