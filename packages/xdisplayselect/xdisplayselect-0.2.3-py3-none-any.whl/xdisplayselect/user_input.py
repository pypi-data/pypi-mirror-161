from collections.abc import Sequence
from typing import cast

import inquirer.shortcuts as inquire


def prompt_list(msg: str, options: Sequence[str], use_dmenu: bool = False) -> str:
    if len(options) == 0:
        raise ValueError("At least 1 option required.")

    if len(options) == 1:
        return options[0]

    if not use_dmenu:
        return inquire.list_input(msg, choices=options)

    raise NotImplementedError()


def prompt_confirm(msg: str, use_dmenu: bool = False) -> bool:
    if not use_dmenu:
        return cast(bool, inquire.confirm(msg))

    raise NotImplementedError()
