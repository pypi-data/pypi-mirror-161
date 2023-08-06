from rich.live import Live
from rich.text import Text

from src.data import check_registration
from src.menu import index_menu, start


def main():
    check_registration()

    group, arrow_pos = start()

    functions = [
        index_menu,
        index_menu,
        index_menu,
    ]

    with Live(group, auto_refresh=False, screen=True) as live:

        choice = 0
        while True:
            choice = functions[choice](live, arrow_pos, group)

            if choice == -1:
                group = Text("END")
                live.update(group, refresh=True)
                break


if __name__ == "__main__":
    main()
