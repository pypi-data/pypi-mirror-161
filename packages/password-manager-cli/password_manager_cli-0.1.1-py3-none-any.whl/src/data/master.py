from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule

from src.utils.crypto import encrypt


def check_registration() -> None:
    path = Path("src/data")
    archive = path / ".env"

    if not archive.exists():
        register(archive)


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
