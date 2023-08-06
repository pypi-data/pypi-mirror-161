# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Utilities for deprecating commons nodes."""
import warnings
from typing import Optional

import forge

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node.documentation import Category
from qctrlcommons.preconditions import check_argument


def deprecated_node(
    updated_node_name: Optional[str] = None, extra_info: Optional[str] = None
):
    """
    Create a decorator to mark a node as deprecated. If the deprecation is only a renaming, the
    deprecated node class can be made a subclass of the new node class and left otherwise empty.

    When you mark a node as deprecated, remember to remove the existing "See Also" references to it
    or redirect them to the node with the updated name.

    Parameters
    ----------
    updated_node_name : str, optional
        The name of the node to use instead of the deprecated node. Defaults to None, in which
        case no alternative is provided in the docstring or when calling the node.
    extra_info : str, optional
        Additional information to provide in the node's docstring and warning when it is called.

    Returns
    -------
    callable
        A callable (decorator) that accepts a node class, replaces its docstring with a deprecation
        notice, and throws a warning when the node is called.

    Example
    -------
    @deprecated_node("new_node_name")  # deprecated 2019/04/14
    class DeprecatedNode(NewNode):
        \"""Deprecated node.\"""

        name = "deprecated_node_name"
    """

    def decorator(node):
        # Replace docstring with deprecation notice.
        docstring = "This node will be removed in the future."
        if updated_node_name is not None:
            docstring += f" Please use :py:func:`{updated_node_name}` instead."
        if extra_info is not None:
            docstring += "\n\n" + extra_info
        node.__doc__ = docstring

        # Mark node as deprecated so it can be skipped in some tests.
        node.is_deprecated = True

        # Ensure the node is in the deprecated documentation category.
        node.categories = [Category.DEPRECATED_OPERATIONS]

        # Update create_node_data to throw a warning if called.
        original_create_node_data = node.create_node_data

        def new_create_node_data(*args, **kwargs):
            warning = f"The '{node.name}' node will be removed in the future."
            if updated_node_name is not None:
                warning += f" Please use '{updated_node_name}' instead."
            if extra_info is not None:
                warning += " " + extra_info
            warnings.warn(warning)
            return original_create_node_data(*args, **kwargs)

        node.create_node_data = new_create_node_data

        return node

    return decorator


# Create unique sentinel values to check for non-passed parameters
# (with __repr__ methods so they display nicely in signatures).
class RequiredValue:
    """
    Sentinel class to label required parameters.
    """

    def __repr__(self):
        return "<RequiredValue>"


class DeprecatedValue:
    """
    Sentinel class to label deprecated parameters.
    """

    def __repr__(self):
        return "<DeprecatedValue>"


REQUIRED_VALUE = RequiredValue()
DEPRECATED_VALUE = DeprecatedValue()


def rename_parameter(old_name: str, new_name: str):
    """
    Create a decorator to mark a parameter as deprecated due to it being renamed. Use this to
    mark an argument as deprecated on a node written only in terms of the new parameter name.
    You can rename multiple parameters by sequentially applying the decorator for each one.

    The following case is not supported by this decorator:
        - Parameter is required and occurs before other required parameters.

    Parameters
    ----------
    old_name : str
        The original name of the deprecated parameter.
    new_name : str
        The parameter name to replace the deprecated one.

    Returns
    -------
    callable
        A callable (decorator) that accepts a node class, adds the old parameter name to its
        parameter list in the docstring and to the forge arguments, and wraps its `create_node_data`
        to pass the updated parameter if the old parameter name is passed (throwing a warning).

    Raises
    ------
    QctrlException
        if the docstring of node does not include a Returns section.

    Example
    -------
    @rename_parameter(  # deprecated 2019/08/24
        old_name="number_of_pulses", new_name="pulse_count"
    )
    class FunctionNode(Node):
        # node definition in terms of only pulse_count
    """

    def decorator(node):
        docstring = node.__doc__
        returns_str = "\n\n    Returns"
        if returns_str not in docstring:
            raise QctrlException(
                f"The docstring of {node.name} does not include a Returns section."
            )

        # Split the docstring after the last parameter.
        docstring, docstring_end = docstring.split(returns_str)
        docstring_end = returns_str + docstring_end

        # Add deprecated parameter to docstring.
        old_parameter_str = (
            f"\n    {old_name} : deprecated"
            "\n        This parameter will be removed in the future,"
            f"\n        please use `{new_name}` instead."
        )
        docstring = docstring + old_parameter_str

        node.__doc__ = docstring + docstring_end

        # Check if the renamed parameter is required (i.e. has an empty default).
        # If so, add a REQUIRED_VALUE default.
        node_args = []
        for forge_arg in node.args:
            if forge_arg.name == new_name:
                is_required = forge_arg.default == forge.empty
                arg_type = forge_arg.type
                if is_required:
                    forge_arg = forge_arg.replace(default=REQUIRED_VALUE)
                default_value = forge_arg.default
            node_args.append(forge_arg)
        node.args = node_args

        # Add old name as a keyword parameter with DEPRECATED_VALUE default.
        node_kwargs = node.kwargs.copy()
        node_kwargs[old_name] = forge.kwarg(
            old_name, type=Optional[arg_type], default=DEPRECATED_VALUE
        )
        node.kwargs = node_kwargs

        # Update create_node_data to:
        # - if called with old_name (a user is using and older version of commons):
        #   pass as new_name and throw a warning.
        # - if both old_name and new_name are passed (unlikely):
        #   throw an error (note that we can't distinguish between passing
        #   the default value for new_name and not passing a value).
        # As the sentinel values are not JSON serializable, we remove old_name
        # from both the node kwargs and the operation kwargs.
        original_create_node_data = node.create_node_data

        def new_create_node_data(*args, **kwargs):
            new_value = kwargs[new_name]
            old_value = kwargs.pop(old_name)

            if old_value is not DEPRECATED_VALUE:
                check_argument(
                    new_value is default_value,
                    f"You can't provide values for both `{new_name}` and `{old_name}`, "
                    f"please use only `{new_name}`.",
                    {new_name: new_value, old_name: old_value},
                )
                warnings.warn(
                    f"The parameter `{old_name}` of `{node.name}` will be "
                    f"removed in the future. Please use `{new_name}` instead."
                )
                kwargs[new_name] = old_value
                operation = kwargs["_operation"]
                operation.kwargs[new_name] = operation.kwargs.pop(old_name)
                return original_create_node_data(*args, **kwargs)

            if is_required:
                check_argument(
                    new_value is not REQUIRED_VALUE,
                    f"You need to provide a value for `{new_name}`.",
                    {new_name: new_value},
                )

            kwargs["_operation"].kwargs.pop(old_name)
            return original_create_node_data(*args, **kwargs)

        node.create_node_data = new_create_node_data

        return node

    return decorator
