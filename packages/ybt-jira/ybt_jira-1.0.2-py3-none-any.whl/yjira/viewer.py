# viewer.py

from datetime import datetime

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table


def make_layout(issues) -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="issues", ratio=1),
    )

    layout["issues"].split(
        Layout(name="1"),
        Layout(name="2"),
        Layout(name="3"),
        Layout(name="4"),
        Layout(name="5"),
    )
    return layout


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]YBT[/b] Board",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")


def make_issue_data(issue) -> Panel:
    issue_data = Table.grid(padding=0)
    issue_data.add_column(style="green", justify="center")
    issue_data.add_column(no_wrap=True)
    issue_data.add_row(
        "Summary: ",
        f"{issue.fields.summary}",
    )
    issue_data.add_row(
        "Status: ",
        f"{issue.fields.status}",
    )
    issue_data.add_row(
        "Priority: ",
        f"{issue.fields.priority}",
    )
    issue_data.add_row(
        "Reporter: ",
        f"{issue.fields.reporter}",
    )
    issue_data.add_row(
        "External ID: ",
        f"{issue.fields.customfield_10127}",
    )

    message_panel = Panel(
        Align.left(issue_data),
        box=box.ROUNDED,
        padding=(1, 2),
        title=f"[b red] {issue}",
        border_style="bright_blue",
    )
    return message_panel


def show(issues):
    """Show issues"""
    console = Console()
    layout = make_layout(issues)

    layout["header"].update(Header())

    i = 1
    for issue in issues:
        layout[str(i)].update(make_issue_data(issue))
        i += 1
    console.print(layout)
