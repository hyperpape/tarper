#!/usr/bin/python3

from collections import defaultdict
from itertools import groupby
from os.path import getsize
from pathlib import Path
import sys
from typing import Any, Dict, List

of_interest = ["default", "swappingwithpermutation", "counted", "binsort", "hillclimb", "mcts", "random"]

no_count = [
    "default",
    "size",
    "permutewithindirectory",
    "binsort",
    "random",
    "swapping",
    "naivesimilarity",
    "nonnaivesimilarity",
    "nonnaivesimilaritythenswap",
    "swappingwithpermutation",
]

class Result:
    def __init__(self, name: str, count: int):
        self.name = name
        self.count = count
        self.size: float = 0
        self.best: float = 1000 ** 6
        self.worst: float = -1

    def __str__(self):
        return f"Result(size={self.size}, best={self.best}, worst={self.worst}"

    def __repr__(self):
        return f"Result(size={self.size}, best={self.best}, worst={self.worst}"


def make_all_tables(srcdir: str) -> List[Any]:
    results = read(srcdir)
    return [make_table(k, rollup(v)) for k, v in results.items()]


def pad(s, dist = 8):
    while len(s) < dist:
        s = ' ' + s
    return s

def make_table(k: str, v: List[Result]) -> str:
    m = sorted(v, key=lambda x: x.size, reverse=True)

    header = "*** " + k
    table_header = "| Method | Iterations | Best | Worst | Average "
    split_line = "|-+-+-+-+-|"
    lines = [header, table_header, split_line]

    for l in m:
        if l.name in of_interest:
            count = str(l.count)
            if l.name in no_count:
                count = "-"
            size = int(l.size)
            table_line = (
                "|"
                + "|".join([pad(l.name, 24), pad(count), pad(str(l.best)), pad(str(l.worst)), pad(str(size))])
                + "|"
            )
            lines.append(table_line)
    return "\n".join(lines)


def rollup(results: List[Result]) -> List[Result]:
    rollups = []
    groups = defaultdict(list)
    for result in results:
        key = result.name + str(result.count)
        if result.name in no_count:
            key = result.name
        groups[key].append(result)
    for k, v in groups.items():
        group = v
        result = Result(group[0].name, group[0].count)
        total: float = 0
        for element in group:
            total += element.size
            if element.size < result.best:
                result.best = element.size
            if element.size > result.worst:
                result.worst = element.size
        result.size = total / len(group)
        rollups.append(result)
    return rollups


def read(srcdir: str) -> Dict[str, List[Result]]:
    results = {}
    for condition in ["gz", "gzdup", "zst", "zstdup"]:
        path = srcdir + "experiment/" + condition + "/"
        files = Path(path).rglob("*")
        results[condition] = [result(file) for file in files]
    return results


def result(file: Path) -> Result:
    size = getsize(file)
    filename = file.parts[-1]
    parts = filename[2:].split("-")
    count_part = filename.split("-")[0]
    count = int(count_part)
    name = parts[1]
    result = Result(name, count)
    result.size = getsize(file)
    return result


if __name__ == "__main__":
    for i in make_all_tables(sys.argv[1]):
        print(i)
