#!/bin/bash
# test
sd=sampledata/proceedings-ceur-ws.txt
rm $sd
./getsamples
grep ">" $sd
