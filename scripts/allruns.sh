#!/bin/bash

set -euo pipefail;

COUNT_OPTIONS="1024 4096 16384 65536"

REPEATED="swapping swappingwithpermutation random mcts"
REPEATED="$REPEATED permutewithindirectory nonnaivesimilarity"
REPEATED="$REPEATED nonnaivesimilaritywithswap binsort hillclimb counted"
ONE_TIME="default by_size"

for option in $REPEATED $ONE_TIME
do
    for i in $(seq 1 3)
    do
	for count in $COUNT_OPTIONS
	do
# python3 src/tarper.py experiment/1 /home/justin/Downloads/StringMatching .gz 1 --all 
	    archive=/home/justin/code/tarper/experiment/gz/"$count"-"$option"-"$i".gz;
	    echo python3 ./src/tarper.py "$archive" /home/justin/Downloads/StringMatching '.gz' "$count" "$option" > commands/"$count"-"$option"-gz-"$i"

	    archive=/home/justin/code/tarper/experiment/zst/"$count"-"$option"-"$i".zst;
	    echo python3 ./src/tarper.py "$archive" /home/justin/Downloads/StringMatchingDup '.zst' "$count" "$option" > commands/"$count"-"$option"-zst-"$i"
	    archive=/home/justin/code/tarper/experiment/gzdup/"$count"-"$option"-"$i".zst;
	    echo python3 ./src/tarper.py "$archive"dup /home/justin/Downloads/StringMatchingDup '.gz' "$count" "$option" > commands/"$count"-"$option"-gzdup-"$i"

	    archive=/home/justin/code/tarper/experiment/zstdup/"$count"-"$option"-"$i".zst;
	    echo python3 ./src/tarper.py "$archive" /home/justin/Downloads/StringMatching '.zst' "$count" "$option" > commands/"$count"-"$option"-zstdup-"$i"
	done
    done
done
