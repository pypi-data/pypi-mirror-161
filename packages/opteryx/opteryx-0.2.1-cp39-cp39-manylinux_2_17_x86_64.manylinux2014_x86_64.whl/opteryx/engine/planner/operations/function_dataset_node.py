# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Blob Reader Node

This is a SQL Query Execution Plan Node.

This Node creates datasets based on function calls like VALUES and UNNEST.
"""
import pyarrow

from typing import Iterable

from opteryx.engine.attribute_types import TOKEN_TYPES
from opteryx.engine import QueryDirectives, QueryStatistics
from opteryx.engine.planner.operations import BasePlanNode
from opteryx.exceptions import SqlError
from opteryx.utils.columns import Columns


def _generate_series(alias, *args):

    from opteryx.utils import intervals, dates

    arg_len = len(args)
    arg_vals = [i[0] for i in args]
    first_arg_type = args[0][1]

    # if the parameters are numbers, generate series is an alias for range
    if first_arg_type == TOKEN_TYPES.NUMERIC:
        if arg_len not in (1, 2, 3):
            raise SqlError("generate_series for numbers takes 1,2 or 3 parameters.")
        return [{alias: i} for i in intervals.generate_range(*arg_vals)]

    # if the params are timestamps, we create time intervals
    if first_arg_type == TOKEN_TYPES.TIMESTAMP:
        if arg_len != 3:
            raise SqlError(
                "generate_series for dates needs start, end, and interval parameters"
            )
        return [{alias: i} for i in dates.date_range(*arg_vals)]

    # if the param is a CIDR, we create network ranges
    if first_arg_type == TOKEN_TYPES.VARCHAR:
        if arg_len not in (1,):
            raise SqlError("generate_series for strings takes 1 CIDR parameter.")

        import ipaddress

        ips = ipaddress.ip_network(arg_vals[0], strict=False)
        return [{alias: str(ip)} for ip in ips]


def _unnest(alias, *args):
    """unnest converts an list into rows"""
    return [{alias: value} for value in args[0][0]]


def _values(alias, *values):
    return values


def _fake_data(alias, *args):

    import os
    import sys

    def _inner(rows, columns):
        for row in range(rows):
            record = {
                f"column_{col}": int.from_bytes(os.urandom(2), sys.byteorder)
                for col in range(columns)
            }
            yield record

    rows, columns = args[0][0], args[1][0]
    rows = int(rows)
    columns = int(columns)
    return list(_inner(rows, columns))


FUNCTIONS = {
    "fake": _fake_data,
    "generate_series": _generate_series,
    "unnest": _unnest,
    "values": _values,
}


class FunctionDatasetNode(BasePlanNode):
    def __init__(
        self, directives: QueryDirectives, statistics: QueryStatistics, **config
    ):
        """
        The Blob Reader Node is responsible for reading the relevant blobs
        and returning a Table/Relation.
        """
        super().__init__(directives=directives, statistics=statistics)
        self._statistics = statistics
        self._alias = config["alias"]
        self._function = config["dataset"]["function"]
        self._args = config["dataset"]["args"]

    @property
    def config(self):  # pragma: no cover
        if self._alias:
            return f"{self._function} => {self._alias}"
        return f"{self._function}"

    @property
    def name(self):  # pragma: no cover
        return "Dataset Constructor"

    def execute(self) -> Iterable:

        data = FUNCTIONS[self._function](self._alias, *self._args)  # type:ignore

        table = pyarrow.Table.from_pylist(data)
        table = Columns.create_table_metadata(
            table=table,
            expected_rows=table.num_rows,
            name=self._function,
            table_aliases=[self._alias],
        )
        yield table
