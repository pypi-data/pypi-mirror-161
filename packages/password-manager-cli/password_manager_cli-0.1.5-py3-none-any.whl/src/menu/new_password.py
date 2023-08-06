from email.message import EmailMessage
from time import sleep

import click
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.text import Text

from src.data.master import master_encrypted
from src.utils import choice_option
from src.utils.crypto import decrypt


def new_pwd() -> int:
    console = Console()
    console.set_alt_screen()
    console.print(Rule("STORE NEW PASSWORD", style="cyan"))

    site = Prompt.ask("Where is the password from?")
    console.print(f"It's from [green]{site}[/]\n")

    if Confirm.ask("Is there a url for it?", default=True):
        url = Prompt.ask("Enter the url")
        console.print(f"The url is [yellow]{url}[/]")
    else:
        url = ""

    user = Prompt.ask("\nWhat is your user?")
    console.print(f"Your user is [cyan]{user}[/]")

    pwd = Prompt.ask("\nWhat is your password?", password=True)
    if Confirm.ask("Want to confirm your password?", default=False):
        console.print(f"Your password is [red]{pwd}[/]")

    for tentativa in range(3):
        master = Prompt.ask(
            "\nWhat is your [red]master[/] password?",
            password=True,
        )
        if decrypt(master_encrypted(), master):
            return

    console.print(
        "\n[prompt.invalid]The password is wrong, redirecting to the menu...",
    )
    sleep(3)
    return
