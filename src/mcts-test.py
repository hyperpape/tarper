from collections import Counter
from mcts import Node


def test_update_depth_1():
    node = Node()
    node.update(["a"], 7)
    node.update(["b"], 5)

    assert node.min == 5
    assert node.max == 7


def test_update_max_min():
    node = Node()
    node.update(["a"], 7)
    node.update(["b"], 5)
    assert node.max == 7
    assert node.min == 5

    node.update(["c"], 9)
    node.update(["d"], 4)
    assert node.max == 9
    assert node.min == 4

    assert node.children["a"].max == 7
    assert node.children["a"].min == 7

    assert node.children["b"].max == 5
    assert node.children["b"].min == 5


def test_best_child():
    node = Node()
    node.update(["a", "e"], 7)
    node.update(["b", "f"], 5)
    node.update(["c", "g"], 9)
    node.update(["d", "h"], 4)
    assert "h" in node.best_child().children.keys()


def test_path_for_best_child():
    node = Node()
    node.update(["a", "e"], 7)
    node.update(["b", "f"], 5)
    node.update(["c", "g"], 9)
    node.update(["d", "h"], 4)
    assert ["d"] == node.best_child().path()


def test_forced_choice():
    node = Node()
    node.update(["a", "b", "c"], 5)
    node.update(["a", "b", "d"], 7)
    node.update(["a", "e", "f"], 2)
    assert "f" in node.choose_path(0.5, 3).parent.children.keys()


def test_choose_child():
    node = Node()
    node.update(["a", "c"], 5)
    node.update(["b", "d"], 2)
    reached = Counter()
    for i in range(10000):
        chosen = node.choose_child(2)
        path = chosen.path()
        reached["".join(path)] += 1
    assert reached["b"] > reached["a"]


def test_choose_path():
    node = Node()
    node.update(["a", "b"], 5)
    node.update(["a", "c"], 2)
    reached = Counter()
    for i in range(10000):
        chosen = node.choose_path(2)
        keys = chosen.parent.children.keys()
        reached[list(keys)[0]] += 1
    print(reached)
    assert reached["b"] > reached["c"]


def test_weights():
    node = Node()
    node.update(["a"], 5)
    node.update(["b"], 7)
    assert node.weight(node.children["a"], 2) > node.weight(node.children["b"], 2)


def test_new_paths():
    node = Node()
    node.update(["a", "b", "c", "d"], 1)
    node.update(["a", "b", "d", "c"], 2)
    node.update(["a", "c", "b", "d"], 3)
    node.update(["a", "c", "d", "b"], 4)
    node.update(["a", "d", "b", "c"], 5)
    node.update(["a", "d", "c", "b"], 6)

    s = set()
    for i in range(10000):
        s.add(tuple(node.new_path(["a", "b", "c", "d"], ["a", "b", "c", "d"], 0)))
    assert len(s) == 6

    s = set()
    for i in range(10000):
        s.add(tuple(node.new_path(["a", "b", "c", "d"], ["a", "b", "c", "d"], 2)))
    assert len(s) == 2


def test_best_path():
    node = Node()
    node.update(["a", "b", "c", "d"], 1)
    node.update(["a", "b", "d", "c"], 2)
    node.update(["a", "c", "b", "d"], 3)
    node.update(["a", "c", "d", "b"], 4)

    assert node.best_path() == ["a", "b", "c", "d"]


def test_prune_tree():
    node = Node()
    node.update(["a", "b", "c"], 1)
    node.update(["a", "d", "e"], 2)
    node.update(["a", "f", "g"], 3)
    node.update(["a", "b", "h"], 4)
    node.update(["a", "d", "i"], 5)
    node.update(["a", "f", "j"], 6)

    node.prune_tree(2)
    assert len(node.children["a"].children.keys()) == 2
    assert "f" not in node.children["a"].children.keys()
