from typing import Optional, IO

from click import UsageError
from click._compat import get_text_stderr
from greap.logger.rich_utils import print


def show(self, file: Optional[IO] = None) -> None:
    if file is None:
        file = get_text_stderr()
    hint = ""
    if self.ctx is not None and self.ctx.command.get_help_option(self.ctx) is not None:
        hint = "[i dim]Try [/i dim][bold #6aa84f]{command} {option}[/bold #6aa84f] [i dim]for help.[/i dim]\n".format(  # noqa: E501
            command=self.ctx.command_path, option=self.ctx.help_option_names[0]
        )
    print(
        "[#a0acec]Welcome to [/#a0acec][i b magenta]Greap :open_hands_medium_skin_tone:"
    )
    if self.ctx is not None:
        print(f":pencil: {self.ctx.get_usage()}\n{hint}")
    print(
        "[bold red]Error:[/bold red] [i]{message}[/i]".format(
            message=self.format_message()
        ),
    )


# patch how usage is printed
UsageError.show = show
