from dotenv import dotenv_values

from .master import check_registration


def master_encrypted() -> str:
    return dotenv_values("./src/data/.env")["MASTER"]
