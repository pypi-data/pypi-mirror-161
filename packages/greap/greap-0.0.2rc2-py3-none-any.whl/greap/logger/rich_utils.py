import click
import logging
from typing import Optional

from rich import print
from rich.console import Console
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich import box
from rich.tree import Tree

from ..timer import Timer


to_emojis = {
    "run": ":play_button: ",
    "help": ":books: ",
    "run-immortal": ":gem: ",
    "run-controller": ":hammer_and_wrench: ",
    "run-load-balancer": ":level_slider: ",
    "backtest": ":test_tube: ",
    "collect-backtest-data": ":package: ",
    "build": ":optical_disk: ",
    "run-connector": ":clinking_glasses: ",
    "run-prefetcher": ":outbox_tray: ",
    "run-backtest-quote-price-feeder": ":open_mailbox_with_raised_flag: ",
}


# NOTE: deprecated
class MyTable(Table):
    def set_row(self, row_index, *renderables):
        def set_cell(column, item):
            if row_index >= len(column._cells):
                raise ValueError("row index exceed column size")
            column._cells[row_index] = item

        for column_index, renderable in enumerate(renderables):
            column = self.columns[column_index]
            set_cell(column, renderable)


# NOTE: deprecated
class RichFormatter(logging.Formatter):
    color = {
        logging.INFO: "#007500",
        logging.DEBUG: "magenta",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "black on red",
    }

    def __init__(self, name: str, display_table: bool, timer: Timer):
        super(RichFormatter, self).__init__()
        self.name = name
        self.display_table = display_table
        self.timer = timer

    def format(self, record):
        time = record.time
        s = "[{asctime}] [bold {color}]{name} {level}[/bold {color}]: {message}".format(
            color=self.color[record.levelno],
            level=record.levelname,
            name=record.name if not self.display_table else "",
            asctime=time.strftime("%Y-%m-%d %H:%M:%S"),
            message=record.msg,
        )
        return s


# NOTE: deprecated
class RichHandler(logging.Handler):
    def __init__(
        self,
        table,
        name,
        level,
        display_table=False,
        log_filepath: Optional[str] = None,
    ):
        super().__init__(level)
        self.table = table
        self.display_table = display_table
        if self.table and display_table:
            self.table.add_row(name, "")
            self.row_index = len(table.rows) - 1
        self.name = name
        self._file = open(log_filepath, "w") if log_filepath else None
        # self.console = Console(file=f)
        self.console = Console()
        # self.console.clear()

    def emit(self, record):
        if self.display_table and self.table:
            self.table.set_row(
                self.row_index,
                f"[bold dim red]{self.name}[/bold dim red]",
                self.format(record),
            )
        else:
            self.console.print(self.format(record))

    def close(self):
        if self._file:
            self._file.close()
        super().close()


class RichGroup(click.Group):
    def get_help(self, ctx):
        t = Table.grid(padding=0, pad_edge=True)
        t.add_column("Row", no_wrap=True)

        ttt = Table.grid(padding=0, pad_edge=True)
        ttt.add_column("Usage", no_wrap=False, width=50)
        ttt.add_column("Details", no_wrap=False, width=60)
        ttt.add_row(
            Align(
                "[b #f8b500]Usage[/b #f8b500]",
                vertical="middle",
                height=2,
            ),
            Align("[b #f8b500]Details[/b #f8b500]", vertical="middle", height=2),
        )
        height = 1
        for i, (n, command) in enumerate(self.commands.items(), start=1):
            if n.startswith("run-"):
                continue
            sub_ctx = command.context_class(command, info_name=n, parent=ctx)
            usage = command.get_usage(sub_ctx)
            usage = usage.replace(
                "[OPTIONS]", "[italic dim #a0acec][OPTIONS][/italic dim #a0acec]"
            )
            cmd_tree = Tree(
                f"[dim #cfdee3]{i}[/dim #cfdee3]. "
                f"{to_emojis[n]} "
                f"[b #c3d825]{usage} [/b #c3d825]",
                guide_style="bright_blue",
            )
            height += 1
            for option in command.params:
                if option.param_type_name == "option":
                    cmd_tree.add(
                        "[dim #a0acec]option: [/dim #a0acec][#ccff99]"
                        f'{", ".join(option.opts)} '
                        "[/#ccff99] [dim #ccff99]"
                        f"<default: "
                        "{option.default}>"
                        "[/dim #ccff99]"
                    )
                    height += 1
            ttt.add_row(cmd_tree, f"[#99cccc]{command.help}[/#99cccc]")
            ttt.add_row("", "")
            height += 1
        t.add_row(self.help)
        t.add_row("", "")
        t.add_row(ttt)
        print(t)


class RichCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super(RichCommand, self).__init__(*args, **kwargs)

    def get_usage(self, ctx):
        pieces = self.collect_usage_pieces(ctx)
        pieces = [
            f"[bold #c3d825]{p}[/bold #c3d825]"
            if p != "[OPTIONS]"
            else "[italic dim #a0acec][OPTIONS][/italic dim #a0acec]"
            for p in pieces
        ]

        return f"[bold #c3d825]{ctx.command_path}[/bold #c3d825] " + " ".join(pieces)

    def get_help(self, ctx):
        print(
            "[#a0acec]Welcome to [/#a0acec][i b magenta]"
            "Greap :open_hands_medium_skin_tone:"
        )
        HELP_WIDTH, TREE_WIDTH = 100, 40  # noqa: 177
        # table = Table.grid(padding=[0,5,0,0], pad_edge=True)
        # table.add_column('tree', min_width=TREE_WIDTH, no_wrap=True)
        usage = self.get_usage(ctx)
        usage = usage.replace(
            "[OPTIONS]", "[italic dim #a0acec][OPTIONS][/italic dim #a0acec]"
        )
        cmd_tree = Tree(
            f"{to_emojis[self.name]} "
            f"[b #c3d825]{usage} [/b #c3d825]\n"
            f"[#99cccc]{self.help}[/#99cccc]",
            guide_style="bright_blue",
            highlight=True,
        )

        for arg in self.params:
            if arg.param_type_name == "argument":
                pass

        for option in self.params:
            if option.param_type_name == "option":
                help_text = format(option.help or "<no description>", HELP_WIDTH)
                cmd_tree.add(
                    "[dim #a0acec]option: [/dim #a0acec][#ccff99]"
                    f'{", ".join(option.opts)} '
                    f"[/#ccff99] [dim #ccff99]<default: {option.default}>[/dim #ccff99]"
                    f"\n[#99cccc]{help_text} [/#99cccc]"
                )

        print(cmd_tree)


def batch(s, w):
    for i in range(0, len(s), w):
        yield s[i : i + w]


def format(s, max_width):
    return "• " + "\n  ".join(batch(s, max_width))


def initialize_table():
    # TODO: Refactor this logic
    table = MyTable(
        show_lines=True,
        show_header=True,
        box=box.MINIMAL_DOUBLE_HEAD,
        title="[i]Welcome to [magenta]Greap[/magenta][/i] :moneybag:",
        border_style="#632619",
        title_style="bold",
        highlight=None,
    )
    table.add_column("[yellow]Component[/yellow] :gear:", no_wrap=True)
    _wra
    table.add_column(
        "[dim cyan]Status[/dim cyan] :horizontal_traffic_light:", no_wrap=False
    )
    table_centered = Align.center(table)
    console = Console()
    console.clear()
    live = Live(table_centered, console=console, screen=False, refresh_per_second=10)
    live.start()
    return table
