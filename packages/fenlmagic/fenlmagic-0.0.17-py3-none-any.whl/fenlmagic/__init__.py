#!/bin/python

"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from __future__ import print_function
import IPython
from IPython.core.error import UsageError
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
    cell_magic,
    line_cell_magic,
)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

import os
import pandas

import kaskada as kda
from kaskada import compute
import kaskada.api.v1alpha.compute_pb2 as pb


class QueryResult(object):
    dataframe: pandas.DataFrame = None

    def __init__(self, query: str, query_response: pb.StreamQueryResponse):
        self.query = query
        self.query_response = query_response

    def set_dataframe(self, dataframe: pandas.DataFrame):
        self.dataframe = dataframe


@magics_class
class FenlMagics(Magics):

    client = None
    tables = {}
    views = {}

    def __init__(self, shell, client):
        super(FenlMagics, self).__init__(shell)
        self.client = client

    @line_magic
    @magic_arguments()
    @argument(
        "--plaintext",
        default=False,
        action="store_true",
        help="Connects to the given endpoint without TLS encryption",
    )
    @argument(
        "--legacy",
        default=False,
        action="store_true",
        help="Uses the legacy compute engine",
    )
    @argument(
        "--endpoint",
        default="api.kaskada.com:50051",
        type=str,
        help="The Kaskada endpoint and port.",
    )
    @argument(
        "--exchange-endpoint",
        default="prod-kaskada.us.auth0.com",
        type=str,
        help="The Auth endpoint to use when obtaining a JWT.",
    )
    @argument(
        "--audience",
        default="https://api.prod.kaskada.com",
        type=str,
        help="The Auth audience to use when obtaining a JWT.",
    )
    @argument(
        "client_id",
        metavar="client-id",
        type=str,
        help="The Kaskada credential Client-ID.",
    )
    @argument(
        "client_secret",
        metavar="client-secret",
        type=str,
        help="The Kaskada credential Client-Secret.",
    )
    def fenl_auth(self, arg):
        "fenl API client id"

        args = parse_argstring(self.fenl_auth, arg)

        self.client = kda.client(
            client_id=args.client_id,
            client_secret=args.client_secret,
            endpoint=args.endpoint,
            exchange_endpoint=args.exchange_endpoint,
            audience=args.audience,
            is_secure=not args.plaintext,
            engine="LEGACY" if args.legacy else None,
        )

    @magic_arguments()
    @argument(
        "--as-view",
        help="adds the body as a view with the given name to all subsequent fenl queries.",
    )
    @argument(
        "--changed-since-time",
        help="Time bound (inclusive) after which results will be produced.",
    )
    @argument(
        "--data-token",
        help="A data token to run queries against. Enables repeatable queries.",
    )
    @argument("--debug", default=False, help="Shows debugging information")
    @argument(
        "--dry-run",
        default=False,
        help="When `True`, the query is validated and if there are no errors, the resultant schema is returned. \
            No actual computation of results is performed.",
    )
    @argument(
        "--experimental",
        help="When `True`, then experimental features are allowed. \
            Data returned when using this flag is not guaranteed to be correct.",
    )
    @argument(
        "--output",
        help='Output format for the query results. One of "df" (default), "json", "parquet" or "redis-bulk". \
            "redis-bulk" implies --result-behavior "final-results"',
    )
    @argument(
        "--preview-rows",
        help="Produces a preview of the data with at least this many rows.",
    )
    @argument(
        "--result-behavior",
        help='Determines which results are returned. \
            Either "all-results" (default), or "final-results" which returns only the final values for each entity.',
    )
    @argument("--var", help="Assigns the body to a local variable with the given name")
    @cell_magic
    @line_cell_magic
    def fenl(self, arg, cell=None):
        "fenl query magic"

        args = parse_argstring(self.fenl, arg)
        dry_run = test_arg(clean_arg(str(args.dry_run)), "true")
        experimental = test_arg(clean_arg(str(args.experimental)), "true")
        output = clean_arg(args.output)
        result_behavior = clean_arg(args.result_behavior)
        preview_rows = clean_arg(args.preview_rows)
        var = clean_arg(args.var)
        view = clean_arg(args.as_view)
        with_views = []

        if cell is None:
            with_views.extend(self.views.values())
            query = arg

        else:
            if view is not None:
                v = pb.WithView(
                    name=view,
                    expression=cell,
                )
                self.views[view] = v
                query = view

            else:
                query = cell.strip()

        with_views.extend(self.views.values())

        limits = {}
        if preview_rows:
            limits["preview_rows"] = int(preview_rows)

        try:
            resp = compute.query(
                query=query,
                with_views=with_views,
                result_behavior="final-results"
                if test_arg(result_behavior, "final-results")
                else "all-results",
                dry_run=dry_run,
                experimental=experimental,
                data_token_id=clean_arg(args.data_token),
                changed_since_time=clean_arg(args.changed_since_time),
                response_as="redis-bulk"
                if test_arg(output, "redis-bulk")
                else "parquet",
                limits=pb.StreamQueryRequest.Limits(**limits),
                client=self.client,
            )
            query_result = QueryResult(query, resp)

            if not dry_run and (test_arg(output, "df") or output is None):
                # TODO: figure out how to support reading from multiple parquet paths
                if len(query_result.query_response.parquet.paths) > 0:
                    df = pandas.read_parquet(
                        query_result.query_response.parquet.paths[0], engine="pyarrow"
                    )
                    if args.debug:
                        query_result.set_dataframe(df)
                    else:
                        query_result.set_dataframe(
                            df.drop(["_time", "_subsort", "_key_hash"], axis=1)
                        )

            if var is not None:
                IPython.get_ipython().push({var: query_result})

            return query_result
        except Exception as e:
            raise UsageError(e)


def load_ipython_extension(ipython):
    if kda.KASKADA_DEFAULT_CLIENT is None:
        if os.getenv("KASKADA_CLIENT_ID") and os.getenv("KASKADA_CLIENT_SECRET"):
            kda.init()

    magics = FenlMagics(ipython, kda.KASKADA_DEFAULT_CLIENT)
    ipython.register_magics(magics)


def clean_arg(arg: str) -> str:
    """
    Strips quotes and double-quotes from passed arguments

    Args:
        arg (str): input argument

    Returns:
        str: cleaned output
    """
    if arg is not None:
        return arg.strip('"').strip("'")
    else:
        return None


def test_arg(arg: str, val: str) -> bool:
    """
    Compares an argument against a test value.
    Returns true when the two strings are equal in a case-insensitive and dash/underscore-insensitive manner.

    Args:
        arg (str): the argument to test
        val (str): the comparison value

    Returns:
        bool: The comparision result.
    """
    if arg is not None and val is not None:
        return arg.replace("_", "-").lower() == val.replace("_", "-").lower()


# def unload_ipython_extension(ipython):
