import jax.numpy as jnp

from pytreeclass import treeclass
from pytreeclass.src.tree_util import (
    is_treeclass,
    is_treeclass_leaf,
    node_count_and_size,
)


@treeclass
class Test:
    a: int = 10


a = Test()
b = (1, "s", 1.0, [2, 3])


@treeclass
class Test2:
    a: int = 1
    b: Test = Test()


def test_is_treeclass():
    assert is_treeclass(a) is True
    assert all(is_treeclass(bi) for bi in b) is False


def test_is_treeclass_leaf():
    assert is_treeclass_leaf(a) is True
    assert all(is_treeclass_leaf(bi) for bi in b) is False
    assert is_treeclass_leaf(Test2()) is False
    assert is_treeclass_leaf(Test2().b) is True


def test_node_count_and_size():
    @treeclass
    class Test:
        a: jnp.ndarray = jnp.array([1.0, 2.0, 3.0])
        b: int = 1

    t = Test()
    assert node_count_and_size(t.b) == (complex(0, 1), complex(28, 0))
    assert node_count_and_size(t.a) == (complex(3, 0), complex(12, 0))
