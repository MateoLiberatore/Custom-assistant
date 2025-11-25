from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.style import Style

console = Console()

STYLE_TITLE = Style(color="#FF8C00", bold=True, underline=True)
STYLE_INFO = Style(color="green")
STYLE_WARNING = Style(color="yellow")
STYLE_ERROR = Style(color="red", bold=True)

def show_help(commands: dict):
    table = Table(title="AVAILABLE COMMANDS")
    table.add_column("Command")
    table.add_column("Description")
    for cmd, desc in commands.items():
        table.add_row(cmd, desc)
    console.print(table)

def confirm_discard():
    return Confirm.ask("Warning: Chat is not saved. Do you want to discard it?")

def prompt_input(prompt_text: str) -> str:
    return Prompt.ask(prompt_text)
