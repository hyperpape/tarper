import random
import sys

from collections import defaultdict
from math import sqrt
from typing import List, Optional, Tuple


class Node:
    """
    Stores data about a subtree of the full mcts tree. The Runner class
    is responsible for doing the actual computations, files manipulation,
    etc.
    """

    def __init__(self):
        self.max = 0
        self.min = -1
        self.key = None
        self.base_order = {}
        self.parent = None
        self.children: DefaultDict[str, Node] = defaultdict(Node)

    def size(self) -> int:
        size = 0
        if len(self.children) == 0:
            return 1
        for child in self.children.values():
            size += child.size()
        return size

    def set_base_order(self, path: List[str]) -> None:
        for i, key in enumerate(path):
            self.base_order[key] = i

    def print_order(self, path: List[str], size) -> None:
        order = [self.base_order[key] for key in path]
        print(str(order) + ": " + str(size))
    
    def update(self, path: List[str], value) -> None:
        """
        Update the tree for a particular path, and value
        """
        current = self
        had_update = False
        for i, key in enumerate(path):
            updated = current.update_value(value)
            if updated and not had_update:
                had_update = True
                print(f"updating #{i} to {value}")
            child = current.children[key]
            # initialize the child as it may be created from the default dict
            if not child.parent:
                child.parent = current
                child.key = key
            current = child
        current.update_value(value)

    def update_value(self, value) -> bool:
        """
        Updates the min/max of this node based on the value.
        Returns True if the value was updated, False otherwise??
        """
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
            child = current.best_child()
            if child is None:
                return current
            current = child
        while current.children:
            current = current.choose_child(ratio)
        return current

    def best_path(self) -> List[str]:
        current = self
        while True:
            child = current.best_child()
            if not child:
                return current.path()
            else:
                current = child

    def best_child(self):  # -> Optional[Tuple[str, Node]]:
        children = [elem for elem in self.children.values() if elem.min == self.min]
        if children:
            return random.choice(children)
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
        """
        Return the path from the current node to the root of the tree.
        """
        path = []
        current = self
        while current:
            if current.key:
                path.append(current.key)
            current = current.parent
        return list(reversed(path))

    def prune_tree(self, count, depth = 0) -> None:
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
                if depth <= 0:
                    count = count - 1
                v.prune_tree(max(count, 1), depth - 1)

    def new_path(
        self, files: List[str], path: List[str], forced_depth: int
    ) -> List[str]:
        keep = random.randrange(max(forced_depth, 1), len(files) - 1)
        path_prefix = path[0:keep]
        trailing = [file for file in files if file not in path_prefix]
        random.shuffle(trailing)
        path_prefix.extend(trailing)
        return path_prefix

    def combined_path(
        self, files: List[str], path: List[str], forced_depth: int
    ) -> List[str]:
        second_path = self.choose_path(5, forced_depth=forced_depth).path()
        combined_path = []
        chosen = set()
        for i, file in enumerate(path):
            if file in chosen:
                continue
            next_file = file
            combined_path.append(next_file)
            chosen.add(next_file)
            if random.randrange(0, 1) < 0.1:
                follower = self.choose_follower(second_path, chosen, file)
                if follower and follower not in chosen:
                    chosen.add(follower)
                    combined_path.append(follower)
        if len(combined_path) != len(files):
            raise ValueError()
        return combined_path

    def choose_follower(
        self, second_path: List[str], chosen: set[str], file: str
    ) -> Optional[str]:
        for j, second_file in enumerate(second_path):
            if second_file == file:
                if j + 1 < len(second_path):
                    return second_path[j + 1]
        return None
