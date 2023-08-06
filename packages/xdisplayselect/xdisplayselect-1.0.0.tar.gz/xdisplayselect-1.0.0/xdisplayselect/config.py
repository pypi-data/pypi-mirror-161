from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self


@dataclass
class Config:
    """
    Class for storing main program configuration.

    Mainly used with argparse to obtain the config from passed CLI arguments,
    using the `parse` classmehod.
    """

    use_dmenu: bool
    restore: bool
    cache: bool
    cache_file: Path
    skip_confirm: bool

    def __post_init__(self) -> None:
        """Perform some data sanitation and initial tasks."""
        # Make sure we expand `~` if present so we don't use it as a relative path and create `~` dir
        self.cache_file = self.cache_file.expanduser()
        # Ensure exitence of the specified directory for the cache file
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        # Ensure existence of the cache file itself
        self.cache_file.touch()

    @classmethod
    def parse(cls) -> Self:
        """Obtain program configuration based on passed CLI arguments."""
        parser = argparse.ArgumentParser(
            prog="displayselect",
            description=textwrap.dedent(
                """
                DisplaySelect is a CLI tool probing xrandr for connected displays, and
                allowing easy interactive user configuration to select which one(s) to
                use, and in what configuration.

                The primary interaction method is using dmenu for user prompts, however
                CLI-only prompts are also supported. After the displays were configured
                for the first time, this configuration is cached and when the same
                setup is detected, this stored configuration can be restored without
                requiring any further user interaction.
                """
            ),
        )
        parser.add_argument(
            "-c",
            "--cli",
            help="Use CLI-only prompts instead of dmenu ones.",
            action="store_true",
        )
        parser.add_argument(
            "-r",
            "--restore",
            help="Use cached configuration for current monitors, if none is found the user will still be prompted.",
            action="store_true",
        )
        parser.add_argument(
            "-C",
            "--no-cache",
            help="Don't store any new configurations into the cache.",
            action="store_true",
        )
        parser.add_argument(
            "-n",
            "--no-confirm",
            help="Don't ask for confirmation before running xrandr command.",
            action="store_true",
        )
        parser.add_argument(
            "-f",
            "--cache-file",
            help="Path to the JSON cache file. (default: %(default)s)",
            type=Path,
            default=Path("~/.cache/xdisplayselect.json"),
        )

        args = parser.parse_args()

        return cls(
            use_dmenu=not args.cli,
            restore=args.restore,
            cache=not args.no_cache,
            cache_file=args.cache_file,
            skip_confirm=args.no_confirm,
        )
