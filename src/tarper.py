import collections
import datetime
import itertools
import os
import random
import subprocess
import sys
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from mcts import Node
import pdb


def candidate_files(path: str) -> Iterable[Tuple[str, str]]:
    for parent, subfolder, files in os.walk(path):
        for file in files:
            yield parent, file


def to_files(pairs: Iterable[Tuple[str, str]]) -> List[str]:
    return [os.path.join(fp[0], fp[1]) for fp in pairs]


def make_archive(name: str, files: Iterable[str], extension: str):
    first, *rest = files
    with open("output", "a") as f:
        if extension == ".gz":
            subprocess.call(["tar", "-cf", name, first], stderr=subprocess.DEVNULL)
            for file in rest:
                subprocess.call(["tar", "-rf", name, file], stderr=subprocess.DEVNULL)
            subprocess.run(["gzip", name])
        elif extension == ".zst":
            subprocess.call(["tar", "-cf", name, first], stderr=subprocess.DEVNULL)
            for file in rest:
                subprocess.call(["tar", "-rf", name, file], stderr=subprocess.DEVNULL)
            subprocess.run(["zstd", "-19", "--long", name])
        else:
            raise ValueError("Unrecognized choice of compression: " + runner.extension)


def permute_within_directory(path: str) -> Iterable[Tuple[str, str]]:
    files = candidate_files(path)
    sublists = itertools.groupby(files, lambda x: x[0])
    for grouper in sublists:
        elems = list(grouper[1])
        random.shuffle(elems)
        for elem in elems:
            yield elem


def order_by_similarity(files: List[str]) -> List[str]:
    similarities = similarity_matrix(files)
    pairs = [(k, v) for k, v in similarities.items()]
    pairs.sort(key=lambda f: f[1], reverse=True)
    order = []
    used: Set[str] = set()
    current = pairs[0][0][0]
    order.append(current)
    next_file = select_next(files, current, used, similarities)
    while next_file:
        used.add(next_file)
        current = next_file
        order.append(current)
        next_file = select_next(files, current, used, similarities)
    return order


def select_next(
    files: List[str],
    current: str,
    used: Set[str],
    similarities: Dict[Tuple[str, str], float],
) -> Optional[str]:
    best_similarity: float = 0
    best = None
    for file in files:
        if file not in used and file != current:
            if (file, current) in similarities:
                similarity = similarities[(file, current)]
            else:
                similarity = similarities[(current, file)]
            if similarity > best_similarity or best_similarity == 0:
                best = file
                best_similarity = similarity
    return best


def similarity_matrix(files: List[str]) -> Dict[Tuple[str, str], float]:
    similarities = {}
    tokenized: List[Tuple[str, Any]] = [
        (file, collections.Counter(words(file, 4))) for file in files
    ]
    for i, file_pair1 in enumerate(tokenized):
        for j, file_pair2 in enumerate(tokenized):
            if i < j:
                continue
            s = similarity(file_pair1[1], file_pair2[1])
            similarities[(file_pair1[0], file_pair2[0])] = s
    return similarities


def most_common(file: str):
    return collections.Counter(words(file)).most_common()


def similarity(words1, words2):
    overlap = 0
    for k, v in words1.items():
        overlap += min(v, words2[k]) * len(k)
    return overlap / (counter_size(words1) + counter_size(words2))


def counter_size(counter):
    return sum((item[1] for item in counter.items()))


def words(file: str, min_length=0):
    with open(file, "r") as f:
        for line in f.readlines():
            for word in line.split(" .;\(\){}[]"):
                if len(word) > min_length:
                    yield word


def sort_by_size(path: str) -> Iterable[Tuple[str, str]]:
    files = candidate_files(path)
    return sorted(list(files), key=lambda f: os.path.getsize(os.path.join(f[0], f[1])))


def swap(files):
    left = random.randrange(0, len(files))
    right = random.randrange(0, len(files))
    left_file = files[left]
    right_file = files[right]
    files[left] = right_file
    files[right] = left_file


class Runner:
    def __init__(self, target_archive, src, extension, count):
        self.target_archive = target_archive
        self.src = src
        self.extension = extension
        self.count = count
        self.options = {
            "swapping": ArchiveMethod(self, "swapping", self.by_swapping),
            "swappingwithpermutaion": ArchiveMethod(
                self, "swappingwithpermutation", self.by_swapping_with_permutation
            ),
            "random": ArchiveMethod(self, "random", self.by_random),
            "mcts": ArchiveMethod(self, "mcts", self.by_mcts),
            "permutewithindirectory": ArchiveMethod(
                self, "permutewithindirectory", self.by_permute_within_directory
            ),
            "default": ArchiveMethod(self, "default", self.by_default),
            "nonnaivesimilarity": ArchiveMethod(
                self, "nonnaivesimilarity", self.by_non_naive_similarity
            ),
            "naivesimilarity": ArchiveMethod(
                self, "naivesimilarity", self.by_naive_similarity
            ),
            "nonnaivesimilaritywithswap": ArchiveMethod(
                self,
                "nonnaivesimilaritythenswap",
                self.by_non_naive_similarity_with_swap,
            ),
            "by_size": ArchiveMethod(self, "size", self.by_size),
            "binsort": ArchiveMethod(self, "binsort", self.by_binsort),
            "hillclimb": ArchiveMethod(self, "hillclimb", self.by_hill_climbing),
            "counted": ArchiveMethod(self, "counted", self.by_counted_iterations),
        }

    def workdir(self):
        return os.path.dirname(self.target_archive)

    def by_swapping(self) -> List[str]:
        files = to_files(candidate_files(self.src))
        return self.by_swapping_files(files)

    def by_swapping_with_permutation(self) -> List[str]:
        file_pairs = list(permute_within_directory(self.src))
        return self.by_swapping_files(to_files(file_pairs))

    def by_permute_within_directory(self) -> List[str]:
        return to_files(list(permute_within_directory(self.src)))

    def by_default(self) -> List[str]:
        return to_files(list(candidate_files(self.src)))

    def by_size(self) -> List[str]:
        return to_files(sort_by_size(self.src))

    def by_random(self) -> List[str]:
        files = to_files(list(candidate_files(self.src)))
        random.shuffle(files)
        return files

    def by_binsort(self) -> List[str]:
        files = subprocess.run(
            ["binsort", self.src], capture_output=True, text=True
        ).stdout.split("\n")
        return [f for f in files if not os.path.isdir(f)]

    def by_naive_similarity(self) -> List[str]:
        files: List[Tuple[str, str]] = list(candidate_files(self.src))
        return to_files(
            sorted(files, key=lambda x: most_common(os.path.join(x[0], x[1])))
        )

    def by_non_naive_similarity(self) -> List[str]:
        files = list(candidate_files(self.src))
        random.shuffle(files)  # why?
        return order_by_similarity([os.path.join(f[0], f[1]) for f in files])

    def by_non_naive_similarity_with_swap(self) -> List[str]:
        files = list(candidate_files(self.src))
        return self.by_swapping_files(self.by_non_naive_similarity())

    def by_swapping_files(self, best_choice: List[str]) -> List[str]:
        best_size = self.compute_size(best_choice, self.extension)
        i = 0
        iters = 0
        while i + 1 < len(best_choice):
            next_choice = list(best_choice)
            left = next_choice[i]
            right = next_choice[i + 1]
            next_choice[i] = right
            next_choice[i + 1] = left
            size = self.compute_size(next_choice, self.extension)
            if size + 1 < best_size:
                best_choice = next_choice
                best_size = size
                i = max(0, i - 3)  # yolo, think harder about bounds
                iters += 1
            i += 1
        return best_choice

    def by_swapping_count(self, files) -> List[str]:
        i = 0
        best_size = self.compute_size(files, self.extension)
        best_choice = files
        while i < self.count:
            i += 1
            with open("output", "a") as f:
                if i % 1000 == 0:
                    now = datetime.datetime.now()
                    msg = f"{now}, did iteration {i}"
                    print(msg, file=f)
            next_choice = list(best_choice)
            swap(next_choice)
            size = self.compute_size(next_choice, extension)
            # making sure it's at least a gap of two, because it seems
            # as if the files generated here sometimes shrink or
            # expand by one byte, not sure why
            if size + 1 < best_size:
                best_choice = next_choice
                files = next_choice
                best_size = size
                with open("output", "a") as f:
                    now = datetime.datetime.now()
                    msg = f"{now}, best_size={best_size} on iteration {i}"
                    print(msg, file=f)
        return best_choice

    def compute_size(self, files: List[str], extension=None) -> int:
        if extension is None:
            extension = self.extension
        if len(files) < 2:
            print(files)
        target = self.workdir() + "/tmpfile.tar"
        make_archive(target, files, extension)
        file_name = target + extension
        size = os.path.getsize(file_name)
        os.remove(file_name)
        return size

    def by_hill_climbing(self) -> List[str]:
        files = to_files(candidate_files(self.src))
        return self.hill_climbing_with_probabilistic_replacement(files)

    # Note that this is only very loosely inspired by mcts, not a faithful
    # implementation
    def by_mcts(self) -> List[str]:
        files = to_files(candidate_files(self.src))
        path_length = len(files)
        tree = self.initialize_mcts(files)
        for i in range(self.count):
            if i % 100 == 0:
                tree.prune_tree(5)
                if i % 1000 == 0:
                    print(f"iteration #{i}")
            depth: int = 0
            if i < self.count // 2:
                node = tree.choose_path(5)
            else:
                depth = len(files) // (self.count // i)
                # hacky: this will waste effort sometimes.
                # better to do a real solution that focuses on interesting cases
                if depth + 3 >= len(files):
                    depth = len(files) - 3
                node = tree.choose_path(5, forced_depth=depth)
            path = node.new_path(files, node.path(), depth)
            size = self.compute_size(path)
            if size < tree.min:
                print(i, size)
            tree.update(path, size)
        return files  # path of best node in the tree

    def initialize_mcts(self, files: List[str]):
        tree = Node()
        for f in files:
            for i in range(5):
                remaining = [file for file in files if file is not f]
                random.shuffle(remaining)
                order = [f]
                order.extend(remaining)
                size = self.compute_size(order)
                tree.update(order, size)
                return tree

    def by_counted_iterations(self) -> List[str]:
        return self.by_swapping_count(to_files(candidate_files(self.src)))

    def hill_climbing_with_probabilistic_replacement(self, files: List[str]):
        state = OptState(files, self.compute_size(files, self.extension))
        with open("output", "a") as output_file:
            while True and state.iterations < self.count:
                if state.iterations % 1000 == 0:
                    now = datetime.datetime.now()
                    msg = f"{now}, did iteration {state.iterations}"
                    print(msg, file=output_file)
                best_candidate_size = sys.maxsize
                for candidate_num in range(4):
                    state.iterations += 1
                    next_choice = list(state.current)
                    swap(next_choice)
                    size = self.compute_size(next_choice, self.extension)
                    if best_candidate_size is None or size < best_candidate_size:
                        best_candidate = next_choice
                        best_candidate_size = size
                if best_candidate_size + 1 < state.best_size:
                    state.best = best_candidate
                    state.best_size = best_candidate_size

                if best_candidate_size < state.current_size:
                    state.current = best_candidate
                    state.current_size = best_candidate_size
                    now = datetime.datetime.now()
                    msg = f"{now}, best_size={state.best_size}, best_size_candidate={best_candidate_size}, current_size={state.current_size} on iteration {state.iterations}"
                    print(msg, file=output_file)
                elif random.random() > 0.95:
                    state.current = best_candidate
                    state.current_size = best_candidate_size
                    now = datetime.datetime.now()
                    msg = f"{now}, switched randomly best_size={state.best_size}, best_size_candidate={best_candidate_size}, current_size={state.current_size} on iteration {state.iterations}"
                    print(msg, file=output_file)
        return state.best

    def run(self, arg):
        if arg == "--all":
            for k in self.options.keys():
                self.options[k]()
        else:
            self.options[arg]()


class OptState:
    def __init__(self, best: List[str], best_size):
        self.best = best
        self.best_size = best_size
        self.current = best
        self.current_size = best_size
        self.iterations = 0


class ArchiveMethod:
    def __init__(self, runner, suffix, method: Callable):
        self.runner = runner
        self.suffix = suffix
        self.method = method

    def __call__(self):
        name = self.runner.target_archive + "_" + self.suffix
        files = self.method.__call__()
        try:
            make_archive(name, files, self.runner.extension)
        except Exception:
            print(files)
            breakpoint()


# usage: tarper.py target_archive source_directory extension iteration_count key
if __name__ == "__main__":
    target_archive = sys.argv[1]
    src = sys.argv[2]
    extension = sys.argv[3]

    runner = Runner(target_archive, src, extension, int(sys.argv[4]))
    runner.run(sys.argv[5])
