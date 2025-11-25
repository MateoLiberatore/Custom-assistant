import sys
import typer
from rich.console import Console
from rich.style import Style

from ..core.chat_manager import ChatManager
from ..core.gemini_service import GeminiChatService
from ..utils.parsing import extract_code_blocks
from ..config import load_config

console = Console()

cfg = load_config()

chat_app = typer.Typer()
config_app = typer.Typer()
main_app = typer.Typer()

# expose as sub-typer groups
main_app.add_typer(chat_app, name="chat", help="Chat management commands")
main_app.add_typer(config_app, name="config", help="Configuration commands")

# Shared manager/service
manager = ChatManager()
service = GeminiChatService(manager.system_prompt, manager.temperature, api_key=cfg.get('GEMINI_API_KEY'))

@chat_app.command("new")
def chat_new(name: str = typer.Option(None, help="Optional name for the new chat")):
    """Start a new chat (optionally set name)."""
    if name:
        manager.set_name(name)
    manager.new_chat()
    service.update_config(system_prompt=manager.system_prompt, temperature=manager.temperature)
    console.print("[green]New chat started.[/green]")

@chat_app.command("name")
def chat_name(name: str):
    """Set the name of current chat."""
    manager.set_name(name)
    console.print(f"[green]Chat name set to:[/] {manager.name}")

@chat_app.command("save")
def chat_save():
    """Save chat to disk."""
    if not manager.name:
        console.print("[red]ERROR: Chat has no name. Use chat name before saving.[/red]")
        raise typer.Exit(code=1)
    history = service.get_full_history()
    msg = manager.save_chat(history)
    console.print(f"[green]{msg}[/green]")

@chat_app.command("list")
def chat_list():
    """List saved chats."""
    chats = manager.get_all_chats()
    if not chats:
        console.print("[yellow]No saved chats.[/yellow]")
        raise typer.Exit()
    for c in chats:
        console.print(f"- {c['name']} (saved_at: {c['saved_at']})")

@chat_app.command("load")
def chat_load(name: str):
    """Load a saved chat by name."""
    try:
        metadata, gemini_history = manager.load_chat(name)
        service.update_config(system_prompt=manager.system_prompt, temperature=manager.temperature)
        # attempt to pass history to service if supported
        service.load_history(gemini_history)
        console.print(f"[green]Chat '{name}' loaded.[/green]")
    except FileNotFoundError:
        console.print(f"[red]ERROR: Chat '{name}' does not exist.[/red]")

@chat_app.command("delete")
def chat_delete(name: str):
    """Delete a saved chat."""
    msg = manager.delete_chat(name)
    console.print(f"[green]{msg}[/green]")

@main_app.command("ask")
def ask(prompt: str = typer.Argument(..., help="Message to send to Gemini")):
    """Send a message to Gemini and print the response."""
    manager.add_message("USER", prompt)
    response = service.send_message(prompt)
    manager.add_message("MODEL", response)
    # Print raw response (could be code blocks)
    parts = extract_code_blocks(response)
    for part in parts:
        if part[0] == "text":
            console.print(part[1])
        elif part[0] == "code":
            from rich.syntax import Syntax
            lang = part[2] if len(part) > 2 else "text"
            syntax = Syntax(part[1], lang, theme="monokai", line_numbers=True)
            console.print(syntax)

@config_app.command("role")
def set_role(text: str):
    """Set system prompt / role for assistant."""
    manager.system_prompt = text
    service.update_config(system_prompt=text)
    console.print(f"[cyan]Role updated:[/] {text}")

@config_app.command("temp")
def set_temp(value: float = typer.Argument(..., help="Temperature between 0.0 and 1.0")):
    """Set generation temperature."""
    if not 0.0 <= value <= 1.0:
        console.print("[red]Error: temperature must be between 0.0 and 1.0[/red]")
        raise typer.Exit(code=1)
    manager.temperature = value
    service.update_config(temperature=value)
    console.print(f"[green]Temperature set to:[/] {value}")
