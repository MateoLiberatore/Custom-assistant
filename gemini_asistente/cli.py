import click
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.style import Style
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv
from pathlib import Path # Necessary import

# KEY CORRECTIONS: Change direct imports to relative (add the dot .)
from .constants import COMMANDS
from .chat_manager import ChatManager
from .gemini_service import GeminiChatService
from .utils import extract_code_blocks

# ==============================================================================
# 1. RICH SETUP AND STYLES
# ==============================================================================

# CRITICAL CORRECTION: Explicit definition of DOTENV_PATH to ensure API key loading.
DOTENV_PATH = Path(__file__).resolve().parent.parent / '.env' 
load_dotenv(dotenv_path=DOTENV_PATH, override=True) 
console = Console()


STYLE_COMMAND = Style(color="#FF8C00", bold=True)
STYLE_ERROR = Style(color="red", bold=True)
STYLE_USER_PROMPT = Style(color="cyan")
STYLE_GEMINI_RESPONSE = Style(color="white")
STYLE_TITLE = Style(color="#FF8C00", bold=True, underline=True)
STYLE_INFO = Style(color="green")
STYLE_WARNING = Style(color="yellow")

# ==============================================================================
# 2. GLOBAL STATE AND SERVICES
# ==============================================================================
manager = ChatManager()
service: GeminiChatService = None

def clear_screen():
    console.clear()

def initialize_service(history: list = None):
    global service
    try:
        service = GeminiChatService(
            manager.system_prompt,
            manager.temperature,
            history=history
        )
    except EnvironmentError as e:
        console.print(f"Critical Error: [red]{e}[/red]", style=STYLE_ERROR)
        sys.exit(1)
    except Exception as e:
        console.print(f"Unexpected initialization error: [red]{e}[/red]", style=STYLE_ERROR)
        sys.exit(1)

# ==============================================================================
# 3. CHAT PRESENTATION FUNCTIONS
# ==============================================================================

def print_message(role: str, content: str):
    if role == "USER":
        style = STYLE_USER_PROMPT
        prefix = "USER:"
    elif role == "MODEL":
        style = STYLE_GEMINI_RESPONSE
        prefix = "GEMINI:"
    else:
        return

    console.print(f"[{style.color.name}]{prefix}[/] ", end="")
    
    parts = extract_code_blocks(content)
    
    for part in parts:
        part_type = part[0]
        
        if part_type == "text":
            console.print(part[1], style=style)
        
        elif part_type == "code":
            code_content = part[1]
            lang = part[2] if len(part) > 2 else "text" 
            
            syntax = Syntax(code_content, lang, theme="monokai", line_numbers=True)
            console.print(syntax)
        
        else:
            console.print(part[1], style=style)

def print_current_chat_state():
    status_text = (
        f"Name: [b]{manager.name or 'New Chat'}[/b] | "
        f"Role: [i]{manager.system_prompt[:40]}...[/i] | "
        f"Temp: [b]{manager.temperature}[/b] | "
        f"Saved: { '[green]Yes[/green]' if manager.is_saved else '[yellow]No[/yellow]' }"
    )
    console.print(Panel(status_text, title=f"[{STYLE_TITLE.color.name}]CURRENT SESSION[/]", border_style="#FF8C00"))
    console.print()

# ==============================================================================
# 4. MENU AND COMMAND FUNCTIONS
# ==============================================================================

def show_help():
    table = Table(title=f"[{STYLE_TITLE.color.name}]AVAILABLE COMMANDS[/]", title_style=STYLE_TITLE)
    table.add_column("Command", style=STYLE_COMMAND, justify="left")
    table.add_column("Description", style=STYLE_GEMINI_RESPONSE, justify="left")
    
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
        
    console.print(table)
    console.print(f"[{STYLE_INFO.color.name}]Type #exit to quit.[/]")
    console.print("-" * 50)


def process_command(command: str, args: str) -> bool:
    cmd = command.lower()
    
    if cmd not in COMMANDS:
        return False
    
    if cmd == "#save":
        if not manager.name:
            new_name = Prompt.ask("Enter the name to save the chat")
            if not new_name:
                console.print(f"[{STYLE_ERROR.color.name}]ERROR: Name not specified.[/]")
                return True
            manager.set_name(new_name)
        
        history_to_save = service.get_full_history()
        msg = manager.save_chat(history_to_save)
        console.print(f"[{STYLE_INFO.color.name}]{msg}[/]")
    
    elif cmd == "#name":
        if not args:
            console.print(f"[{STYLE_ERROR.color.name}]ERROR: Usage: #name NewName[/]")
            return True
        manager.set_name(args)
        console.print(f"[{STYLE_INFO.color.name}]Chat name changed to[/] [b]{manager.name}[/b]")
    
    elif cmd == "#new":
        if not manager.is_saved and manager.history:
            if not Confirm.ask(f"[{STYLE_WARNING.color.name}]Warning: Chat is not saved. Do you want to discard it?[/]"):
                return True
        new_chat()
        
    elif cmd == "#delete":
        if manager.is_saved:
            if Confirm.ask(f"[{STYLE_WARNING.color.name}]Are you sure you want to delete the chat '{manager.name}' from disk?[/]"):
                msg = manager.delete_chat(manager.name)
                console.print(f"[{STYLE_INFO.color.name}]{msg}[/]")
                new_chat()
        else:
            console.print(f"[{STYLE_ERROR.color.name}]ERROR: You can only delete saved chats. Use #new to discard.[/]")

    elif cmd == "#role":
        if not args:
            console.print(f"[{STYLE_ERROR.color.name}]ERROR: Usage: #role New role for the assistant[/]")
            return True
        manager.system_prompt = args
        service.update_config(system_prompt=args)
        console.print(f"[{STYLE_INFO.color.name}]Role updated to:[/][i] {args}[/i]")

    elif cmd == "#temp":
        try:
            temp = float(args)
            if not (0.0 <= temp <= 1.0):
                raise ValueError
            manager.temperature = temp
            service.update_config(temperature=temp)
            console.print(f"[{STYLE_INFO.color.name}]Temperature adjusted to:[/][b] {temp}[/b]")
        except ValueError:
            console.print(f"[{STYLE_ERROR.color.name}]ERROR: Temperature must be a number between 0.0 and 1.0.[/]")

    elif cmd == "#menu":
        main_menu()
    
    elif cmd == "#chats":
        chat_history_menu()
    
    elif cmd == "#help":
        show_help()

    elif cmd == "#exit":
        if not manager.is_saved and manager.history:
            if not Confirm.ask(f"[{STYLE_WARNING.color.name}]Warning: Chat is not saved. Do you want to discard it and exit?[/]"):
                return True
        sys.exit(0)
    
    return True

def new_chat():
    manager.new_chat()
    initialize_service()
    clear_screen()
    console.print(f"[{STYLE_INFO.color.name}]--- New Conversation Started! ---[/]")
    print_current_chat_state()

def load_chat(chat_name: str):
    try:
        metadata, gemini_history = manager.load_chat(chat_name)
        initialize_service(history=gemini_history)
        clear_screen()
        console.print(f"[{STYLE_INFO.color.name}]--- Conversation '{chat_name}' Loaded ---[/]")
        for msg in manager.history:
             print_message(msg['role'], msg['content'])

    except FileNotFoundError:
        console.print(f"[{STYLE_ERROR.color.name}]ERROR: Chat '{chat_name}' does not exist.[/]")
    except Exception as e:
        console.print(f"[{STYLE_ERROR.color.name}]ERROR loading chat:[/]{e}")

def chat_history_menu():
    clear_screen()
    
    while True:
        console.print(Panel("Select a chat or type part of the name/role to filter.", title=f"[{STYLE_TITLE.color.name}]CHAT HISTORY[/]", border_style="#FF8C00"))
        
        search_query = Prompt.ask("Search/Filter (Enter to see all, #menu to return)")
        
        if search_query.lower() == "#menu":
            return main_menu()

        filtered_chats = manager.get_filtered_chats(search_query)

        if not filtered_chats:
            console.print(f"[{STYLE_WARNING.color.name}]No chats found with the criteria.[/]")
            continue

        table = Table(title=f"[{STYLE_TITLE.color.name}]Chats Found ({len(filtered_chats)})[/]", title_style=STYLE_TITLE)
        table.add_column("ID", style=Style(bold=True, color="yellow"))
        table.add_column("Chat Name", style=Style(color="white"))
        table.add_column("Role (Context)", style=Style(color="cyan"))
        table.add_column("Saved", style=Style(color="green"))

        chat_map = {}
        for i, chat in enumerate(filtered_chats):
            chat_id = str(i + 1)
            table.add_row(chat_id, chat['name'], chat['role'][:50] + "...", chat['saved_at'][:10])
            chat_map[chat_id] = chat['name']

        console.print(table)
        
        selection = Prompt.ask("ID to load, #delete ID, #menu, #new")

        if selection.lower() == "#menu":
            return main_menu()
        
        if selection.lower() == "#new":
            return new_chat()
        
        if selection.lower().startswith("#delete"):
            try:
                parts = selection.split()
                if len(parts) < 2: raise ValueError
                chat_id_to_delete = parts[1]
                chat_name_to_delete = chat_map[chat_id_to_delete]
                
                if Confirm.ask(f"[{STYLE_WARNING.color.name}]Are you sure you want to delete '{chat_name_to_delete}'?[/]"):
                    msg = manager.delete_chat(chat_name_to_delete)
                    console.print(f"[{STYLE_INFO.color.name}]{msg}[/]")
                    clear_screen() 
                    continue
            except (KeyError, ValueError):
                console.print(f"[{STYLE_ERROR.color.name}]ERROR: Usage: #delete valid ID.[/]")
                continue
        
        if selection in chat_map:
            load_chat(chat_map[selection])
            return
        
        console.print(f"[{STYLE_ERROR.color.name}]Invalid selection.[/]")
        clear_screen()

def main_menu():
    clear_screen()
    
    menu_content = (
        f"[{STYLE_GEMINI_RESPONSE.color.name}]1. New Chat[/]\n"
        f"[{STYLE_GEMINI_RESPONSE.color.name}]2. Chat History (with search)[/]\n"
        f"[{STYLE_GEMINI_RESPONSE.color.name}]3. Exit application[/]"
    )
    
    menu_panel = Panel(
        menu_content,
        title=f"[{STYLE_TITLE.color.name}]MAIN MENU[/]",
        border_style="#FF8C00"
    )
    console.print(menu_panel)
    
    choice = Prompt.ask("Select an option", choices=["1", "2", "3"])
    
    if choice == "1":
        new_chat()
    elif choice == "2":
        chat_history_menu()
        main_loop() 
    elif choice == "3":
        sys.exit(0)

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        clear_screen()
        initialize_service()
        main_menu()
        main_loop()

def main_loop():
    global service
    
    while True:
        try:
            user_input = Prompt.ask(f"[{STYLE_USER_PROMPT.color.name}]You[/]")
            
            if not user_input.strip():
                continue

            if user_input.startswith("#"):
                parts = user_input.split(maxsplit=1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                if process_command(command, args):
                    continue

            with console.status(f"[{STYLE_INFO.color.name}]Waiting for Gemini response...[/]") as status:
                response_text = service.send_message(user_input)
            
            manager.add_message("USER", user_input)
            manager.add_message("MODEL", response_text)

            print_message("MODEL", response_text)
            
            if manager.is_saved:
                 manager.save_chat(service.get_full_history())
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interruption detected.[/]")
            process_command("#exit", "")
        except Exception as e:
            console.print(f"[{STYLE_ERROR.color.name}]UNEXPECTED ERROR in the loop:[/]{e}")

if __name__ == "__main__":
    cli()