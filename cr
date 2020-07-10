#!/bin/bash
# WF 2020-07-10
# Crossref extraction with jq
sampledir=sampledata
cat $sampledir/crossref-*.json | jq .message.items[].title
