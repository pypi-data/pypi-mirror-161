import json
from itertools import cycle
from pprint import pformat
from typing import List, Optional

import click
import sqlalchemy as sa
from click.core import Group
from dynamic_imports import class_instances_from_module, import_module

from . import schedule
from .models import ScheduledTask
from .tables import SCHEMA_NAME, task_errors_table, task_runs_table
from .utils import get_engine, systemctl

cli = Group("task-flows", chain=True)


@cli.command()
def init_db():
    """Create any tables that do not currently exist in the database."""
    with get_engine().begin() as conn:
        if not conn.dialect.has_schema(conn, schema=SCHEMA_NAME):
            click.echo(click.style(f"Creating schema '{SCHEMA_NAME}'", fg="cyan"))
            conn.execute(sa.schema.CreateSchema(SCHEMA_NAME))
        for table in (
            task_runs_table,
            task_errors_table,
        ):
            click.echo(click.style(f"Checking table: {table.name}", fg="cyan"))
            table.create(conn, checkfirst=True)
    click.echo(click.style("Done!", fg="green"))


@cli.command()
@click.option("-p", "--pattern", required=False)
def show_timers(pattern: Optional[str] = None):
    _pattern = "task_flow*"
    if pattern:
        _pattern += pattern.lstrip("*")
    systemctl("list-timers", _pattern)


@cli.command()
@click.option(
    "-n", type=int, required=False, help="Number of most recent tasks to show."
)
def history(n: Optional[int]):
    with get_engine().begin() as conn:
        task_runs = list(
            conn.execute(
                sa.select(task_runs_table).order_by(task_runs_table.c.started)
            ).fetchall()
        )
        if n:
            task_runs = task_runs[-n:]
        task_runs = [dict(r) for r in task_runs]
    colors = cycle(["bright_green", "bright_blue"])
    for t in task_runs:
        click.echo(click.style(pformat(t), fg=next(colors)))


@cli.command()
@click.argument("tasks_file")
@click.option("-t", "--task", "task_names", multiple=True)
def create(tasks_file: str, task_names: Optional[List[str]] = None):
    if tasks_file.endswith(".py"):
        if not (tasks := class_instances_from_module(tasks_file, ScheduledTask)):
            # check for a list named 'tasks' if no variables are class instnaces.
            if not isinstance(
                (tasks := import_module(tasks_file).__dict__.get("tasks")), list
            ):
                raise ValueError(f"Could not fild tasks in file: {tasks_file}")
    elif tasks_file.endswith(".json"):
        # JSON file should have one task, or a list of tasks.
        if not isinstance((tasks := json.loads(tasks_file.read_text())), list):
            tasks = [tasks]
        tasks = [ScheduledTask(**t) for t in tasks]
    if task_names:
        tasks = [t for t in tasks if t.task_name in task_names]
    click.echo(
        click.style(f"Creating {len(tasks)} tasks from {tasks_file}.", fg="cyan")
    )
    for task in tasks:
        schedule.create_scheduled_task(task)
    click.echo(click.style("Done!", fg="green"))


@cli.command()
@click.argument("tasks_file")
def remove(task_name: str):
    schedule.remove_scheduled_task(task_name)
    click.echo(click.style("Done!", fg="green"))


@cli.command()
@click.argument("tasks_file")
def enable(task_name: str):
    schedule.enable_scheduled_task(task_name)
    click.echo(click.style("Done!", fg="green"))


@cli.command()
@click.argument("tasks_file")
def disable(task_name: str):
    schedule.disable_scheduled_task(task_name)
    click.echo(click.style("Done!", fg="green"))
