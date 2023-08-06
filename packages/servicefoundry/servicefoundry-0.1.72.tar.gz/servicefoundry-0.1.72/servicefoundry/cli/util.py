import functools
import sys
import zipfile

import rich_click as click
from requests.exceptions import ConnectionError
from rich.padding import Padding
from rich.panel import Panel

from servicefoundry.cli.console import console
from servicefoundry.cli.const import IS_DEBUG, MAX_WIDTH
from servicefoundry.lib.exceptions import BadRequestException, ConfigurationException


def setup_rich_click():
    click.rich_click.STYLE_ERRORS_SUGGESTION = "blue italic"
    click.rich_click.MAX_WIDTH = MAX_WIDTH
    click.rich_click.SHOW_ARGUMENTS = True
    click.rich_click.USE_RICH_MARKUP = True
    click.rich_click.STYLE_HELPTEXT = ""


def handle_exception(exception):
    if IS_DEBUG:
        console.print_exception(show_locals=True)
    if isinstance(exception, BadRequestException):
        print_error(
            f"[cyan bold]status_code[/] {exception.status_code}\n"
            f"[cyan bold]message[/]     {exception.message}"
        )
    elif isinstance(exception, ConnectionError):
        print_error(f"Couldn't connect to Servicefoundry.")
    elif isinstance(exception, ConfigurationException):
        print_error(f"[cyan bold]message[/]     {exception.message}")
    else:
        console.print(f"[red][bold]Error:[/] {str(exception)}[/]")


def handle_exception_wrapper(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            handle_exception(e)
            sys.exit(1)

    return inner


def print_error(message):
    text = Padding(message, (0, 1))
    console.print(
        Panel(
            text,
            border_style="red",
            title="Command failed",
            title_align="left",
            width=click.rich_click.MAX_WIDTH,
        )
    )


def print_message(message):
    text = Padding(message, (0, 1))
    console.print(
        Panel(
            text,
            border_style="cyan",
            title="Success",
            title_align="left",
            width=click.rich_click.MAX_WIDTH,
        )
    )


def unzip_package(path_to_package, destination):
    with zipfile.ZipFile(path_to_package, "r") as zip_ref:
        zip_ref.extractall(destination)
