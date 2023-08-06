import datetime
import functools

from rich import box
from rich import print_json as _rich_print_json
from rich.table import Table

from servicefoundry.cli.config import CliConfig
from servicefoundry.cli.console import console
from servicefoundry.cli.const import DISPLAY_DATETIME_FORMAT
from servicefoundry.internal.util import json_default_encoder

print_json = functools.partial(
    _rich_print_json, highlight=False, default=json_default_encoder
)


def get_table(title):
    return Table(title=title, show_lines=False, safe_box=True, box=box.MINIMAL)


def stringify(x):
    if isinstance(x, datetime.datetime):
        return x.astimezone().strftime(DISPLAY_DATETIME_FORMAT)
    elif isinstance(x, str):
        return x
    else:
        return str(x)


def print_list(title, items, columns=None):
    if CliConfig.get("json"):
        print_json(data=items)
        return

    table = get_table(title)

    if items:
        if not columns:
            columns = items[0].keys()
        for column in columns:
            no_wrap = column in ["id", "fqn"]
            table.add_column(column, justify="left", overflow="fold", no_wrap=no_wrap)

    for item in items:
        row = []
        for c in columns:
            row.append(stringify(item[c]))
        table.add_row(*row)
    console.print(table)


def print_obj(title, item, columns=None):
    if CliConfig.get("json"):
        print_json(data=item)
        return

    table = get_table(title)

    if not columns:
        columns = item.keys()

    # transpose
    keys, columns = columns, ["key", "value"]

    for column in columns:
        no_wrap = column in ["id", "fqn"]
        table.add_column(column, justify="left", overflow="fold", no_wrap=no_wrap)
    for key in keys:
        table.add_row(f"[bold]{stringify(key)}[/]", stringify(item[key]))
    console.print(table)
