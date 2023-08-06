from __future__ import annotations

import functools
import inspect
from dataclasses import dataclass

import jax

from .tree_base import explicitTreeBase, implicitTreeBase, treeBase
from .tree_indexer import treeIndexer
from .tree_op_base import treeOpBase


def treeclass(*args, **kwargs):
    """Class JAX  compaitable decorator for `dataclass`"""

    def wrapper(cls, op: bool, field_only: bool):
        user_defined_init = "__init__" in cls.__dict__

        dCls = dataclass(
            unsafe_hash=True, init=not user_defined_init, repr=False, eq=False
        )(cls)

        base_classes = (dCls, treeBase)
        base_classes += (treeOpBase, treeIndexer) if op else ()
        base_classes += (explicitTreeBase,) if field_only else (implicitTreeBase,)

        newCls = type(cls.__name__, base_classes, {})

        return jax.tree_util.register_pytree_node_class(newCls)

    if len(args) > 0 and inspect.isclass(args[0]):
        return wrapper(args[0], True, False)

    elif len(args) == 0 and len(kwargs) > 0:
        op = kwargs["op"] if "op" in kwargs else True
        field_only = kwargs["field_only"] if "field_only" in kwargs else False
        return functools.partial(wrapper, op=op, field_only=field_only)
