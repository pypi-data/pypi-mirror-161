from __future__ import annotations

import copy
from typing import Any

import jax
import jax.numpy as jnp
from jax.tree_util import tree_flatten, tree_leaves, tree_map, tree_unflatten

from pytreeclass.src.decorator_util import dispatch
from pytreeclass.src.tree_util import is_treeclass_leaf_bool


def node_setter(lhs: Any, where: bool, set_value):
    """Set pytree node value.

    Args:
        lhs: Node value.
        where: Conditional.
        set_value: Set value of shape 1.

    Returns:
        Modified node value.
    """
    # do not change non-chosen values
    # assert isinstance(where, bool)

    if isinstance(lhs, jnp.ndarray):
        return jnp.where(where, set_value, lhs)
    else:
        return set_value if where else lhs


def node_getter(lhs, where):
    # not jittable as size can changes
    # does not change pytreestructure ,

    if isinstance(lhs, jnp.ndarray):
        return lhs[where]
    else:
        # set None to non-chosen non-array values
        return lhs if where else None


def param_indexing_getter(model, *where: tuple[str, ...]):
    if model.frozen:
        return model

    modelCopy = copy.copy(model)

    for field in model.__dataclass_fields__.values():
        value = modelCopy.__dict__[field.name]
        excluded_by_type = isinstance(value, str)
        excluded_by_meta = ("static" in field.metadata) and field.metadata["static"] is True  # fmt: skip
        excluded = excluded_by_type or excluded_by_meta
        if field.name not in where and not excluded:
            modelCopy.__dict__[field.name] = None

    return modelCopy


def param_indexing_setter(model, set_value, *where: tuple[str]):
    @dispatch(argnum=1)
    def _param_indexing_setter(model, set_value, *where: tuple[str]):
        raise NotImplementedError(f"Invalid set_value type = {type(set_value)}.")

    @_param_indexing_setter.register(float)
    @_param_indexing_setter.register(int)
    @_param_indexing_setter.register(complex)
    @_param_indexing_setter.register(jnp.ndarray)
    def set_scalar(model, set_value, *where: tuple[str]):
        if model.frozen:
            return model

        modelCopy = model
        for field in model.__dataclass_fields__.values():
            value = modelCopy.__dict__[field.name]

            excluded_by_type = isinstance(value, str)
            excluded_by_meta = ("static" in field.metadata) and field.metadata["static"] is True  # fmt: skip
            excluded = excluded_by_meta or excluded_by_type
            if field.name in where and not excluded:
                modelCopy.__dict__[field.name] = node_setter(value, True, set_value)
        return modelCopy

    # @_param_indexing_setter.register(type(model))
    # def set_model(model, set_value, *where: tuple[str]):
    #     raise NotImplemented("Not yet implemented.")

    return _param_indexing_setter(model, set_value, *where)


def boolean_indexing_getter(model, where):
    if model.frozen:
        return model

    lhs_leaves, lhs_treedef = model.flatten_leaves
    where_leaves, where_treedef = tree_flatten(where)
    lhs_leaves = [
        node_getter(lhs_leaf, where_leaf)
        for lhs_leaf, where_leaf in zip(lhs_leaves, where_leaves)
    ]

    return jax.tree_unflatten(lhs_treedef, lhs_leaves)


def boolean_indexing_setter(model, set_value, where):
    if model.frozen:
        return model

    lhs_leaves, lhs_treedef = tree_flatten(model)
    where_leaves, rhs_treedef = tree_flatten(where)
    lhs_leaves = [
        node_setter(lhs_leaf, where_leaf, set_value=set_value,)
        for lhs_leaf, where_leaf in zip(lhs_leaves, where_leaves)  # fmt: skip
    ]

    return tree_unflatten(lhs_treedef, lhs_leaves)


class treeIndexer:
    @property
    def at(self):
        class indexer:
            @dispatch(argnum=1)
            def __getitem__(inner_self, *args):
                raise NotImplementedError(
                    f"indexing with type{(tuple(type(arg) for arg in args))} is not implemented."
                )

            @__getitem__.register(str)
            @__getitem__.register(tuple)
            def __param_getitiem__(inner_self, *args):
                # indexing by param name
                flatten_args = tree_leaves(args)
                if not all(isinstance(arg, str) for arg in flatten_args):
                    raise ValueError("Invalid indexing argument")

                class getterSetterIndexer:
                    def get(getter_setter_self):
                        # select by param name
                        return param_indexing_getter(self, *flatten_args)

                    def set(getter_setter_self, set_value):
                        # select by param name
                        return param_indexing_setter(
                            copy.copy(self), set_value, *flatten_args
                        )

                    def apply(getter_setter_self, func):
                        return tree_map(func, getter_setter_self.get())

                    def add(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x + set_value)

                    def multiply(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x * set_value)

                    def divide(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x / set_value)

                    def power(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x**set_value)

                    def min(getter_setter_self, set_value):
                        return getter_setter_self.apply(
                            lambda x: jnp.minimum(x, set_value)
                        )

                    def max(getter_setter_self, set_value):
                        return getter_setter_self.apply(
                            lambda x: jnp.maximum(x, set_value)
                        )

                return getterSetterIndexer()

            @__getitem__.register(type(self))
            def __model_getitiem__(inner_self, arg):
                # indexing by model

                if not all(is_treeclass_leaf_bool(leaf) for leaf in tree_leaves(arg)):
                    raise ValueError("model leaves argument must be boolean.")

                class getterSetterIndexer:
                    def get(getter_setter_self):
                        # select by class boolean x[x>1]
                        return boolean_indexing_getter(self, arg)

                    def set(getter_setter_self, set_value):
                        # select by class boolean
                        return boolean_indexing_setter(self, set_value, arg)

                    def apply(getter_setter_self, func):
                        return tree_map(func, getter_setter_self.get())

                    def add(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x + set_value)

                    def multiply(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x * set_value)

                    def divide(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x / set_value)

                    def power(getter_setter_self, set_value):
                        return getter_setter_self.apply(lambda x: x**set_value)

                    def min(getter_setter_self, set_value):
                        return getter_setter_self.apply(
                            lambda x: jnp.minimum(x, set_value)
                        )

                    def max(getter_setter_self, set_value):
                        return getter_setter_self.apply(
                            lambda x: jnp.maximum(x, set_value)
                        )

                return getterSetterIndexer()

        return indexer()

    def __getitem__(self, *args):
        # alias for .at[].get()
        return self.at.__getitem__(*args).get()
