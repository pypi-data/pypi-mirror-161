"""
Tools for programatically manipulating / adding to the namespace.
"""

import inspect
import sys
import types
from typing import Optional, List, Any, NamedTuple


class AugmentedClassMap(NamedTuple):
    """Container of how the augmented classes are mapped"""

    name: str
    original: Any
    augmented: Any


def create_module(name, description, context=None):
    """Dynamically create a python module"""
    module = types.ModuleType(name, description)
    context = context if context is not None else {}
    module.__dict__.update(context)
    return module


def get_subclass_members(module, parent):
    """Get the members of a module which are subclasses of `parent`, excluding
    `parent` itself.

    Args:
        module: The module to find classes within.
        parent: The parent class to search for subclasses of. NB `parent`
          itself will also be filtered out.

    Returns:
        A list of subclasses of `parent` exported from module `module`.
    """

    def _predicate(obj):
        try:
            return (
                issubclass(obj, parent)
                and obj is not parent
                and not obj.__name__.startswith("_")
            )
        except TypeError:
            return False

    return inspect.getmembers(module, _predicate)


def get_instances(module, instance):
    """Get the members of a module which are instances of `instance`.

    Args:
        module: The module to find instances within.
       instance: The parent class to search for subclasses of. NB `parent`
          itself will also be filtered out.

    Returns:
        A list of instances of `instance` exported from module `module`.
    """

    def _predicate(obj):
        return isinstance(obj, instance)

    return inspect.getmembers(module, _predicate)


def create_augmented_classes(
    module: object,
    parent: type,
    class_factory: callable,
    ignore: Optional[List[object]] = None,
) -> List[AugmentedClassMap]:
    """Using `class_factory`, create modified classes of any subclasses of
    `parent` found in `module` and set them in the namespace of `caller`.

    Args:
        caller: The name of the caller module (available as `__name__`).
        module: The module to search for subclasses of `parent`.
        parent: The parent class for discovering classes to augment.
        class_factory: A callable which receives a class, performs operations
          with that class, then returns a new class.

    Notes:
        Type of `module` should be `module`, but this is not available through
        the builtins or `typing` library...
    """
    mappings = []
    ignore = ignore if ignore is not None else []
    for name, cls in get_subclass_members(module, parent):
        if name in ignore:
            continue
        new_cls = class_factory(cls)
        mappings.append(
            AugmentedClassMap(name=cls.__name__, original=cls, augmented=new_cls)
        )
    return mappings


def extend_module(caller: str, mappings: List[AugmentedClassMap]):
    """
    Add attributes to a python module that is already imported.

    """
    for mapping in mappings:
        setattr(sys.modules[caller], mapping.name, mapping.augmented)
