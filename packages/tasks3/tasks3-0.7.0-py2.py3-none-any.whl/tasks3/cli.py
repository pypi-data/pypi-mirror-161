"""Console script for tasks3."""
import sys

import tasks3
import tasks3.db

import click
import sqlalchemy

from pathlib import Path
from typing import Callable, Optional, Iterable, List

from tasks3.config import config, OutputFormat
from tasks3.db import Task


@click.group()
@click.option(
    "--db",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=config.db_path,
    show_default=True,
    help="Location of tasks database.",
)
@click.version_option()
@click.pass_context
def main(ctx: click.core.Context, db: Path):
    """tasks3 is a commandline tool to create and manage tasks and todo lists"""

    ctx.ensure_object(dict)
    config.db_path = db
    engine = sqlalchemy.create_engine(config.db_uri)
    tasks3.db.init(db_engine=engine)
    ctx.obj["config"] = config
    ctx.obj["engine"] = engine
    return 0


@main.command()
@click.option(
    "--id",
    type=str,
    help="Filter by id."
    "You can pass /partial-id/ to search for all tasks whose id contains partial-id.",
)
@click.option("-T", "--title", type=str, help="Search by Title")
@click.option(
    "-u",
    "--urgency",
    type=click.IntRange(min=0, max=4, clamp=True),
    help="Filter by urgency.",
)
@click.option(
    "-i",
    "--importance",
    type=click.IntRange(min=0, max=4, clamp=True),
    help="Filter by importance.",
)
@click.option("-t", "--tags", multiple=True, help="Filter by tags.")
@click.option(
    "-f",
    "--folder",
    type=click.Path(readable=False, path_type=Path),
    help="Filter by delegated folder.",
)
@click.option("-d", "--description", type=str, help="Search in description.")
@click.option(
    "-o",
    "--output-format",
    type=click.Choice([fmt.value for fmt in OutputFormat]),
    default=config.search_output_format,
    show_default=True,
    help="Output format.",
)
@click.pass_context
def search(
    ctx: click.core.Context,
    id: Optional[str],
    title: Optional[str],
    urgency: Optional[int],
    importance: Optional[int],
    tags: Optional[List[str]],
    folder: Optional[Path],
    description: Optional[str],
    output_format: str,
):
    """Search for tasks"""
    engine = ctx.obj["engine"]
    if folder:
        folder = str(folder.expanduser().resolve())
    results: List[Task] = tasks3.search(
        db_engine=engine,
        id=id,
        title=title,
        urgency=urgency,
        importance=importance,
        tags=tags,
        folder=folder,
        description=description,
    )
    output_format = OutputFormat(output_format)
    fmt = __fmt(output_format)
    for task in results:
        click.echo(fmt(self=task))


@main.command()
@click.option(
    "-o",
    "--output-format",
    type=click.Choice([fmt.value for fmt in OutputFormat]),
    default=config.show_output_format,
    help="Output format.",
    show_default=True,
)
@click.argument("id", type=str, required=False)
@click.pass_context
def show(ctx: click.core.Context, output_format: str, id: str):
    """Show the task in the specified FORMAT

    ID is the id of the Task to be printed;
    if not specified, all tasks in current directory are printed.
    """
    engine = ctx.obj["engine"]
    fmt = __fmt(OutputFormat(output_format))
    if id is None:
        tasks = tasks3.search(db_engine=engine, folder=str(Path.cwd()))
    else:
        tasks = tasks3.search(db_engine=engine, id=id)[:1]
    for task in tasks:
        click.echo(fmt(self=task))
    pass


@main.command()
@click.option("-T", "--title", default=None, help="New title for this Task.")
@click.option(
    "-u",
    "--urgency",
    type=click.IntRange(min=0, max=4, clamp=True),
    default=None,
    help="New urgency for this Task. " "Higher is more urgent.",
)
@click.option(
    "-i",
    "--importance",
    type=click.IntRange(min=0, max=4, clamp=True),
    default=None,
    help="New importance for this Task. " "Higher is more important.",
)
@click.option("-t", "--tags", multiple=True, default=[], help="Tags for the Task.")
@click.option(
    "-f",
    "--folder",
    type=click.Path(readable=False, path_type=Path),
    default=None,
    help=("Delegate this Task to this directory or file."),
)
@click.option(
    "-d", "--description", default=None, help="New description for this Task."
)
@click.option(
    "--confirm",
    default=False,
    is_flag=True,
    help="Confirm before overwriting task.",
)
@click.argument("id", type=str)
@click.pass_context
def edit(
    ctx: click.core.Context,
    title: str,
    urgency: int,
    importance: int,
    tags: Iterable[str],
    folder: Path,
    description: Optional[str],
    confirm: bool,
    id: str,
):
    """Edit a Task

    ID is the id of the Task to be edited.
    """
    engine = ctx.obj["engine"]
    search_results = tasks3.search(db_engine=engine, id=id)
    if len(search_results) != 1:
        click.echo(f"Couldn't uniquely find Task with id={id}.", err=True)
        return 1
    if confirm:
        task = search_results[0].yaml()
        new_task = tasks3.edit(
            db_engine=engine,
            id=id,
            title=title,
            urgency=urgency,
            importance=importance,
            tags=tags,
            folder=folder,
            description=description,
            dry_run=True,
        ).yaml()
        click.confirm(
            f"Existing:\n{task}\n"
            f"Updated:\n{new_task}\n"
            "Are you sure you want to update?",
            abort=True,
            default=True,
        )
    task = tasks3.edit(
        db_engine=engine,
        id=id,
        title=title,
        urgency=urgency,
        importance=importance,
        tags=tags,
        folder=folder,
        description=description,
    )
    click.echo(f"Updated Task:\n{task.short()}")


@main.command()
@click.option(
    "-y",
    "--yes",
    default=False,
    is_flag=True,
    help="Delete task without confirmation.",
)
@click.argument("id", type=str)
@click.pass_context
def remove(ctx: click.core.Context, yes: bool, id: str):
    """Remove a Task

    ID is the id of the Task to be removed.
    """
    engine = ctx.obj["engine"]
    if not yes:
        task = tasks3.search(db_engine=engine, id=id)
        if len(task) != 1:
            click.echo(f"Couldn't uniquely find Task with id={id}.", err=True)
            return 1
        task = task[0]
        click.confirm(
            f"{task.yaml()}\nAre you sure you want to delete this Task?",
            abort=True,
            default=False,
        )
    task = tasks3.remove(db_engine=engine, id=id)
    click.echo(f"Removed Task: {task.short()}")


@main.command()
@click.option(
    "-T", "--title", default="Give a Title to this Task.", help="Title of the Task."
)
@click.option(
    "-u",
    "--urgency",
    type=click.IntRange(min=0, max=4, clamp=True),
    default=2,
    show_default=True,
    help="Level of urgency of the Task. " "Higher is more urgent.",
)
@click.option(
    "-i",
    "--importance",
    type=click.IntRange(min=0, max=4, clamp=True),
    default=2,
    show_default=True,
    help="Level of importance of the Task. " "Higher is more important.",
)
@click.option("-t", "--tags", multiple=True, default=[], help="Tags for the Task.")
@click.option(
    "-f",
    "--folder",
    type=click.Path(readable=False, path_type=Path),
    default=Path.cwd(),
    help=(
        "Delegate Task to a specified directory or file.  "
        "[default: current working directory]"
    ),
)
@click.option(
    "-d", "--description", default="", help="A short description of the Task."
)
@click.option(
    "--yes",
    default=False,
    is_flag=True,
    help="Create task without confirmation?",
)
@click.pass_context
def add(
    ctx: click.core.Context,
    title: str,
    urgency: int,
    importance: int,
    tags: Iterable[str],
    folder: Path,
    description: Optional[str],
    yes: bool,
):
    """Add a new task"""
    engine = ctx.obj["engine"]
    description = description.replace("\\n", "\n").replace("\\t", "\t")
    task = Task(
        title=title,
        urgency=urgency,
        importance=importance,
        tags=tags,
        folder=str(folder.expanduser().resolve()),
        description=description,
    )
    if not yes:
        click.confirm(
            f"{task.yaml()}\nAre you sure you want to add this task?",
            abort=True,
            default=True,
        )
    tasks3.add(task, db_engine=engine)
    click.echo(f"Added Task:\n{task.short()}")


@main.command()
@click.pass_context
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def shell(ctx: click.core.Context, shell: str):
    """
    Integrate with your shell

    This command will generate a script to integrate with the specified shell.
    Evaluate the script to setup the integration.

        Ex. eval "$(tasks3 shell zsh)"
    """
    if shell == "bash":
        click.echo("function _chpwd_tasks3() { tasks3 show -o oneline; }")
        click.echo('function cd () { builtin cd "$@"; _chpwd_tasks3; }')
    elif shell == "zsh":
        click.echo("function _chpwd_tasks3() { tasks3 show -o oneline; }")
        click.echo("chpwd_functions+=(_chpwd_tasks3)")
    elif shell == "fish":
        click.echo("function _chpwd_tasks3; tasks3 show -o oneline; end")
        click.echo("function cd; builtin cd $argv; _chpwd_tasks3; end")


@main.group()
@click.pass_context
def db(ctx: click.core.Context):
    """Manage tasks3's database"""
    pass


@db.command()
@click.confirmation_option(prompt="Are you sure you want to purge all tasks?")
@click.pass_context
def purge(ctx: click.core.Context):
    """Purge all tasks from the database"""
    pass


@db.command()
@click.confirmation_option(prompt="Are you sure you want to drop the database?")
@click.pass_context
def drop(ctx: click.core.Context):
    """Drop the databse"""
    pass


@db.command()
@click.confirmation_option(prompt="Are you sure you want to move the database?")
@click.argument(
    "dest_db",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default=config.db_path,
)
@click.pass_context
def move(ctx: click.core.Context, dest_db: str):
    """Move tasks database to DEST_DB

    DEST_DB will be overwriten if it already exists.
    """
    pass


def __fmt(format: OutputFormat) -> Callable[[Task], str]:
    """
    Return a function that formats a Task object according to the specified format.

    :param format: The format to use.
    """
    if format == OutputFormat.oneline:
        fmt = Task.one_line
    elif format == OutputFormat.short:
        fmt = Task.short
    elif format == OutputFormat.yaml:

        def _fmt(self):
            return Task.yaml(self=self) + "\n"

        fmt = _fmt
    elif format == OutputFormat.json:
        fmt = Task.json
    return fmt


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
