from rich.console import Console
from rich.syntax import Syntax
from rich.style import Style

console = Console()

STYLE_USER_PROMPT = Style(color="cyan")
STYLE_GEMINI_RESPONSE = Style(color="white")

def print_message(role: str, content: str, extract_fn):
    if role == "USER":
        style = STYLE_USER_PROMPT
        prefix = "USER:"
    elif role == "MODEL":
        style = STYLE_GEMINI_RESPONSE
        prefix = "GEMINI:"
    else:
        return

    console.print(f"{prefix} ", end="")

    parts = extract_fn(content)
    for part in parts:
        if part[0] == 'text':
            console.print(part[1], style=style)
        elif part[0] == 'code':
            lang = part[2] if len(part) > 2 else 'text'
            syntax = Syntax(part[1], lang, theme='monokai', line_numbers=True)
            console.print(syntax)
        else:
            console.print(part[1], style=style)
