import click
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from src.utils import choice_option


def index_menu() -> int:

    group, arrow_pos = start()

    with Live(group, auto_refresh=False, screen=True) as live:

        live.update(group, refresh=True)
        while True:
            key = click.getchar()
            choice = choice_option(key, arrow_pos)
            if choice is not None:
                if choice == 2:
                    return -1
                return choice

            group = Group(
                Rule("MENU"),
                Align(gen_index(arrow_pos, key), "center"),
            )

            live.update(group, refresh=True)


def gen_index(arrow_pos: list, key: str) -> Panel:

    if key in ("\x1b[B", "s", "S"):
        arrow_pos[0] += 1
    elif key in ("\x1b[A", "w", "W"):
        arrow_pos[0] -= 1

    if arrow_pos[0] > 2:
        arrow_pos[0] = 0
    elif arrow_pos[0] < 0:
        arrow_pos[0] = 2

    linha = arrow_pos[0]

    opt_a = "View registered passwords\n"
    opt_b = "Register new passwords\n"
    opt_c = "Exit"
    selected = "> "
    not_selected = "  "

    options = [not_selected, not_selected, not_selected]
    options[linha] = selected

    linha_1 = Text(options[0] + opt_a)
    linha_2 = Text(options[1] + opt_b)
    linha_3 = Text(options[2] + opt_c)
    linhas = [linha_1, linha_2, linha_3]
    linhas[linha].stylize("bold green", 0, 1)

    menu = Text(justify="left")
    menu.append(linha_1)
    menu.append(linha_2)
    menu.append(linha_3)

    return Panel.fit(menu)


def start() -> tuple:

    arrow_pos = [0]
    group = Group(
        Rule("MENU"),
        Align(gen_index(arrow_pos, ""), "center"),
    )

    return group, arrow_pos
