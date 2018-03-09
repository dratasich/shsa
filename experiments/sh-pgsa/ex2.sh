#!/bin/bash
# profilehooks has been adapted to create this type of output!
# line 780 of profilehooks.py (csv like output):
# print("%s,"
#       "%d,%.6f" % (
#           funcname, self.ncalls,
#           self.totaltime)
#       )

echo "%depth, model, shsa, shsa_n, shsa_et, dfs, dfs_n, dfs_et, orr, orr_n, orr_et" > ex2.csv


n=10  # number of ex2.py runs per model
m=100  # different models (only one is generated for a ex2.py run)
a=0.2
depths1="2 4 6 8"  # different depth
depths2="10 12 14 16"  # different depth
depths3="18"  # different depth

for d in $depths1
do
    # run experiments with m different models
    for i in $(seq "$m")
    do
        # run experiment n times (one model)
        params="-n $n -b 2 -d $d -a $a rss_once orr dfs_mem"
        res=$(PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex2.py $params | grep -A 3 "measurements" | tail -n 3)
        echo "$d,$i,"$res | sed -e "s/ /,/g" >> ex2.csv
    done
done

for d in $depths2
do
    # run experiments with m different models
    for i in $(seq "$m")
    do
        # run experiment n times (one model)
        params="-n $n -b 2 -d $d -a $a rss_once orr"
        res=$(PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex2.py $params | grep -A 2 "measurements" | tail -n 2)
        echo "$d,$i,"$res | sed -e "s/ /,-,-,-,/g" >> ex2.csv
    done
done

for d in $depths3
do
    # run experiments with m different models
    for i in $(seq "$m")
    do
        # run experiment n times (one model)
        params="-n $n -b 2 -d $d -a $a rss_once"
        res=$(PYTHONPATH=../shsa python3 -O ../shsa/benchmark/ex2.py $params | grep -A 1 "measurements" | tail -n 1)
        echo "$d,$i,"$res",-,-,-,-,-,-" >> ex2.csv
    done
done
