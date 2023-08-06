import subprocess
from collections.abc import Sequence
from typing import cast

import inquirer.shortcuts as inquire


def _dmenu_prompt(msg: str, options: Sequence[str]) -> str:
    # Dmenu allows users to send something custom outside of options
    # if that happens, ask again a few times.
    for _ in range(3):
        proc = subprocess.run(["dmenu", "-p", msg], input="\n".join(options).encode("utf-8"), capture_output=True)
        out = proc.stdout.decode("utf-8").removesuffix("\n")
        print(f"Got: {out!r}")
        if out in options:
            return out
        print("Invalid option entered, try again")
    else:
        raise ValueError("Invalid option picked!")


def prompt_list(msg: str, options: Sequence[str], use_dmenu: bool = False) -> str:
    if len(options) == 0:
        raise ValueError("At least 1 option required.")

    if len(options) == 1:
        return options[0]

    if not use_dmenu:
        return inquire.list_input(msg, choices=options)

    return _dmenu_prompt(msg, options)


def prompt_confirm(msg: str, use_dmenu: bool = False) -> bool:
    if not use_dmenu:
        return cast(bool, inquire.confirm(msg))

    return _dmenu_prompt(msg, ["yes", "no"]) == "yes"
