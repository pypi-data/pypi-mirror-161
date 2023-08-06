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
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

from graphql import (
    DocumentNode,
    parse,
)

from qctrlcommons.exceptions import QctrlGqlException


def _raise_qctrl_gql_exception(data: Any):
    """Raises a `QctrlGqlException`. For use in lambdas."""
    raise QctrlGqlException(data)


def check_query_errors(
    query: Union[str, DocumentNode],
    result: dict,
    handle_root_error: Optional[Callable] = None,
    handle_query_error: Optional[Callable] = None,
):
    """Checks for any errors, including query-level errors, returned
     from the query request.

    Parameters
    ----------
    query: Union[str,DocumentNode]
        The query which was executed; either as a string or the
        compiled document object
    result: dict
        The result of the query execution, as returned from
        gql.Client.execute
    handle_root_error: Optional[Callable]
        Hook function called if a root level error is found. The
        callable should accept a single argument which is the query
        result. Default behaviour is to raise a QctrlGqlException.
    handle_query_error: Optional[Callable]
        Hook function called if any query level errors are found. The
        callable should accept two arguments - the query key and the
        query result. Default behaviour is to raise a
        QctrlGqlException.
    """

    # use default error handler for root errors
    def raise_root_error(result):
        if handle_root_error is None:
            return _raise_qctrl_gql_exception(result["errors"])
        return handle_root_error(result)

    if result.get("errors"):
        raise_root_error(result)

    # convert query string to document node
    if isinstance(query, str):
        query = parse(query)

    # use default error handler for query errors
    def raise_query_error(key, result):
        if handle_query_error is None:
            return _raise_qctrl_gql_exception(result["errors"])
        return handle_query_error(key, result)

    # search result for query errors
    for definition_node in query.definitions:
        for node in definition_node.selection_set.selections:
            if node.alias:
                query_key = node.alias.value
            else:
                query_key = node.name.value

            if result.get(query_key, {}).get("errors"):
                raise_query_error(query_key, result[query_key])
