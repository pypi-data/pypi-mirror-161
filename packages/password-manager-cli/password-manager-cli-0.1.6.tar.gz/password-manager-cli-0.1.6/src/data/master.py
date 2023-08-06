from pathlib import Path

from dotenv import dotenv_values
from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule

from src.utils.crypto import decrypt, encrypt

path = Path(__file__).absolute().parent
archive = path / "personal_data" / ".env"


def check_registration() -> None:

    if not archive.exists():
        register(archive)
    else:
        login()


def register(archive: Path) -> None:
    console = Console()
    console.set_alt_screen()
    console.print(Rule("REGISTER", style="red"))

    while True:
        password = Prompt.ask(
            "Please enter a password [cyan](must be at least 5 characters)",
            password=True,
        )
        if len(password) >= 5:
            break
        console.print("[prompt.invalid]password too short")
    console.print("Registred!\n", style="bold green")

    archive.touch()
    archive.write_text(f"MASTER={encrypt(password)}")


def login() -> None:
    console = Console()
    console.set_alt_screen()
    console.print(Rule("LOGIN", style="cyan"))

    while True:
        password = Prompt.ask(
            "Please enter your password",
            password=True,
        )
        if decrypt(master_encrypted(), password):
            break

        console.print("[prompt.invalid]wrong password")


def master_encrypted() -> str:
    return dotenv_values(archive)["MASTER"]
