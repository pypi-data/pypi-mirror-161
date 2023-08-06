import click
from rich.live import Live
from rich.text import Text

import src.utils
from src.menu import gen_index, index_menu, start

def main():

    group, arrow_pos = start()

    functions = [
        index_menu,
        index_menu,
        index_menu,
    ]

    with Live(group, auto_refresh=False) as live:

        choice = 0
        while True:
            choice = functions[choice](live, arrow_pos, group)

            if choice == -1:
                group = Text("END")
                live.update(group, refresh=True)
                break

if __name__ == "__main__":
    main()