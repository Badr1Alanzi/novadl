import sys

import typer

from novadl import __version__
from novadl.cli.commands import (
    audio,
    clear_history,
    config,
    doctor,
    download,
    history,
    info,
    update,
    version,
)
from novadl.cli.menu import run as interactive_menu
from novadl.presentation.console import console
from novadl.presentation.display import show_welcome

app = typer.Typer(
    name="novadl",
    help="NovaDL - أداة تحميل فيديوهات وصوت من الإنترنت من سطر الأوامر.",
    no_args_is_help=False,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
    add_completion=False,
)

app.command(name="download")(download)
app.command(name="audio")(audio)
app.command(name="info")(info)
app.command(name="update")(update)
app.command(name="config")(config)
app.command(name="version")(version)
app.command(name="history")(history)
app.command(name="clear-history")(clear_history)
app.command(name="doctor")(doctor)


def main() -> None:
    if len(sys.argv) <= 1:
        show_welcome()
        interactive_menu()
    else:
        show_welcome()
        app()


if __name__ == "__main__":
    main()
