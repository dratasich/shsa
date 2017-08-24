#!/bin/bash

# stash unstaged changes
git stash -u -q --keep-index

# run unittests (incl pep8)
python3 -m unittest discover 2> test.log
# get first line, containing results, removing passed testcases
res=$(head -n 1 test.log | tr -d '.')
# count occurences of 'E' and 'F'
nume=$(echo "$res" | tr -c -d 'F' | wc -c)
numf=$(echo "$res" | tr -c -d 'E' | wc -c)
rm -f test.log

echo "ERROR: $nume"
echo "FAIL: $numf"

# git unstash
git stash pop -q

# run pycodestyle for all files
pycodestyle . > test.log
numc=$(cat test.log | wc -l)
if (( numc > 0 )); then
    echo "PEP-8: $numc (all files)"
fi
rm -f test.log

# final notice about checks
echo ""
if (( nume > 0 || numf > 0 )); then
    echo "!!! Fix errors before you commit !!!"
else
    echo "You're save to commit :)"
fi
echo ""
