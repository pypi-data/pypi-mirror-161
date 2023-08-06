def choice_option(key: int, arrow_pos: int) -> int | None:
    if key == "\r":
        choice, arrow_pos[0] = arrow_pos[0], 0
        return choice
    elif key in ("\x1b", "q", "Q"):
        return -1
    else:
        None
