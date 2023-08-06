from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from xdisplayselect.monitor import ConnectedMonitor, MonitorJson
from xdisplayselect.user_input import prompt_confirm, prompt_list

if TYPE_CHECKING:
    from typing_extensions import Self


class MonitorConfigJson(TypedDict):
    monitors: list[MonitorJson]
    cmd_args: list[str]


@dataclass
class MonitorConfig:
    monitors: list[ConnectedMonitor]
    cmd_args: list[str]

    def to_json(self) -> MonitorConfigJson:
        monitors = [monitor.as_json() for monitor in self.monitors]
        return MonitorConfigJson(monitors=monitors, cmd_args=self.cmd_args)

    def store_config(self, config_file: Path) -> None:
        with config_file.open("r") as fp:
            contents = fp.read()

        stored_configs: list[MonitorConfigJson] = json.loads(contents) if contents else []
        this_config = self.to_json()

        # Check if this configuration isn't already present
        for config in stored_configs:
            if config["monitors"] == this_config["monitors"]:
                # TODO: Allow overriding
                raise ValueError("Configuration for these monitors already present.")

        stored_configs.append(this_config)

        with config_file.open("w") as fp:
            json.dump(stored_configs, fp)

    @classmethod
    def load_config(cls, monitors: Iterable[ConnectedMonitor], config_file: Path) -> Self:
        with config_file.open("r") as fp:
            contents = fp.read()

        stored_configs: list[MonitorConfigJson] = json.loads(contents) if contents else []
        monitor_conf = [monitor.as_json() for monitor in monitors]

        for config in stored_configs:
            if config["monitors"] == monitor_conf:
                return cls(list(monitors), config["cmd_args"])
        raise ValueError("Requested monitor setup isn't known yet")

    @staticmethod
    def _setup_monitor_against(monitor: ConnectedMonitor, monitor_reference: ConnectedMonitor) -> list[str]:
        if prompt_confirm(f"Mirror {monitor.name} with {monitor_reference.name}?"):
            # We should optimize the mirroring for the resolution of the primary monitor, meaning
            # we may need to be scaling the resolution on the secondary (mirrored) monitor
            scale_x = round(monitor.resolution[0] / monitor.resolution[0], 2)
            scale_y = round(monitor.resolution[1] / monitor.resolution[1], 2)

            args = ["--output", monitor.name, "--same-as", monitor_reference.name, "--scale", f"{scale_x}x{scale_y}"]
        else:
            direction = prompt_list(
                f"What side of {monitor_reference.name} should {monitor.name} be?", ["left", "right"]
            )
            args = [
                "--output",
                monitor.name,
                f"--{direction}-of",
                monitor_reference.name,
                "--auto",
                "--scale",
                "1.0x1.0",
            ]

        return args

    @classmethod
    def _prompt_for_setup_cmd(cls, monitors: Iterable[ConnectedMonitor]) -> list[str]:
        """Generate xrandr command arguments for setting up given monitors"""
        # Group monitors by name for ease of usage
        mon_dct = {mon.name: mon for mon in monitors}

        primary_monitor_name = prompt_list("Select primary monitor:", [mon.name for mon in monitors])
        primary_monitor = mon_dct[primary_monitor_name]

        args = ["xrandr", "--output", primary_monitor.name, "--scale", "1.0x1.0"]

        configured = {primary_monitor}
        unconfigured = {mon for mon in monitors if mon is not primary_monitor}
        while len(unconfigured) != 0:
            # Let the user pick which still unconfigured monitor to handle next
            # we don't auto-pick, because that monitor may require some other still unconfigured one
            # as reference (to mirror against, or choose extend direction against)
            next_mon_name = prompt_list("Select next monitor to configure", [mon.name for mon in unconfigured])
            next_mon = mon_dct[next_mon_name]
            reference_mon_name = prompt_list(
                f"Select monitor to configure {next_mon.name} against", [mon.name for mon in configured]
            )
            reference_mon = mon_dct[reference_mon_name]

            new_args = cls._setup_monitor_against(next_mon, reference_mon)
            args.extend(new_args)

            unconfigured.remove(next_mon)
            configured.add(next_mon)

        return args

    @classmethod
    def prompt_for_setup(cls, monitors: Iterable[ConnectedMonitor]) -> Self:
        cmd_args = cls._prompt_for_setup_cmd(monitors)
        return cls(list(monitors), cmd_args)
