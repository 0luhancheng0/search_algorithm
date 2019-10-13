#!/bin/bash
logfile=./log.txt
inputs=$(ls INPUT)
for i in $inputs
do
    seq=$(basename $i ".txt" | tail -c 2 | head -c 1)
    echo "test case ${seq}" >> $logfile
    echo "DLS output" >> $logfile
	# the time is not recorded to logfile
    time python planpath.py INPUT/$i OUTPUT/output${seq}.txt 3 D | tee -a $logfile
    echo "A output" >> $logfile
    time python planpath.py INPUT/$i OUTPUT/output${seq}.txt 3 A | tee -a $logfile
done
