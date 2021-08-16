import random
import sys

from collections import defaultdict
from math import sqrt
from typing import List, Optional, Tuple


class Node:
    def __init__(self):
        self.max = 0
        self.min = -1
        self.key = None
        self.parent = None
        self.children: DefaultDict[str, Node] = defaultdict(Node)

    def update(self, path: List[str], value) -> None:
        current = self
        had_update = False
        for i, key in enumerate(path):
            updated = current.update_value(value)
            if updated and not had_update:
                had_update = True
                # print(f"updating #{i} to {value}")
            child = current.children[key]
            if not child.parent:
                child.parent = current
                child.key = key
            current = child
        current.update_value(value)

    def update_value(self, value) -> bool:
        if self.max < value:
            self.max = value
        if self.min > value:
            self.min = value
            return True
        if self.min == -1:
            self.min = value
        return False

    def choose_path(self, ratio: float, forced_depth: int = 0):  # -> Node:
        current = self
        for i in range(forced_depth):
            child = self.best_child()
            if child is None:
                return current
        while current.children:
            current = current.choose_child(ratio)
        return current

    def best_child(self):  # -> Optional[Tuple[str, Node]]:
        children = [elem for elem in self.children.values() if elem.min == self.min]
        if children:
            return random.choice(children)
        breakpoint()
        return None

    def choose_child(self, ratio: float):  # -> Node:
        max_prob = 0
        best_child = None
        weights = [self.weight(child, ratio) for child in self.children.values()]

        best_child = random.choices(list(self.children.values()), weights)
        return best_child[0]

    def weight(self, child, ratio: float) -> int:
        # quality in [0, 1]
        if self.max == self.min:
            return 1
        quality = (self.max - child.min) / (self.max - self.min)
        # factor in [0, (1 - 1/n)]
        factor = quality * (1 - (1 / ratio))
        return (1 / ratio) + factor

    def path(self) -> List[str]:
        path = []
        current = self
        while current:
            if current.key:
                path.append(current.key)
            current = current.parent
        return list(reversed(path))

    def prune_tree(self, count) -> None:
        values = sorted([v.min for (k, v) in self.children.items()])[:count]
        if values:
            boundary = values[-1]
            new_children = {
                k: v for (k, v) in self.children.items() if v.min <= boundary
            }
            self.children = defaultdict(Node)
            for k, v in new_children.items():
                self.children[k] = v
            for v in self.children.values():
                v.prune_tree(count)

    def mutate(self) -> List[str]:
        if not self.parent:
            pass
        return []

    def new_path(
        self, files: List[str], path: List[str], forced_depth: int
    ) -> List[str]:
        keep = random.randrange(max(forced_depth, 1), len(files) - 1)
        path_prefix = path[0:keep]
        trailing = [file for file in files if file not in path_prefix]
        random.shuffle(trailing)
        path_prefix.extend(trailing)
        return path_prefix
