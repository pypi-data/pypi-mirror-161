from rich.align import Align
from rich.console import Group
from rich.rule import Rule

from .index_menu import gen_index


def start() -> tuple:

    arrow_pos = [0]
    group = Group(
        Rule("MENU"),
        Align(gen_index(arrow_pos, ""), "center"),
    )

    return group, arrow_pos
    