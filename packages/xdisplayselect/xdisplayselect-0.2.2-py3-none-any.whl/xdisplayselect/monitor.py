from __future__ import annotations

import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal, Optional, Protocol, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import Self


class MonitorJson(TypedDict):
    name: str
    resolution: list[int]


class ConnectedMonitor(Protocol):
    name: str
    connected: Literal[True]
    resolution: tuple[int, int]

    def as_json(self) -> MonitorJson:
        ...


class DisconnectedMonitor(Protocol):
    name: str
    connected: Literal[False]
    resolution: None


@dataclass(frozen=True)
class Monitor:
    name: str
    connected: bool
    resolution: Optional[tuple[int, int]]

    def as_json(self) -> MonitorJson:
        if self.resolution is None:
            raise ValueError("Disconnected monitors (without resolution) can't be serialized into json.")
        return MonitorJson(name=self.name, resolution=list(self.resolution))

    @staticmethod
    def _iter_monitor_configs(xrandr_output: str) -> Iterator[str]:
        """Parse the xrandr output and iterate the relevant output for given monitor."""
        cur_raw = []
        for line in xrandr_output.split("\n"):
            if line.startswith("Screen"):  # Ignore screen lines
                continue
            if not line.startswith(" ") and len(cur_raw) != 0:  # If there's no indentation, this is a new monitor line
                yield "\n".join(cur_raw)
                cur_raw = []
            cur_raw.append(line)

    @classmethod
    def _from_raw(cls, raw_xrandr_output: str) -> Self:
        """Construct a monitor instance from raw xrandr output regarding that monitor."""
        lines = raw_xrandr_output.split("\n")
        words = lines[0].split(" ")
        name = words[0]
        connected = words[1] == "connected"
        if connected:
            _resolution_line = lines[1].strip(" ")
            _str_resolution = _resolution_line.split(" ")[0]
            _str_resolutions = _str_resolution.split("x")
            resolution = (int(_str_resolutions[0]), int(_str_resolutions[1]))
        else:
            resolution = None

        return cls(name, connected, resolution)

    @classmethod
    def get_xrandr_monitors(cls) -> list[Self]:
        """Run xrandr and use the output to produce info about individual monitors."""
        proc = subprocess.run(["xrandr", "-q"], stdout=subprocess.PIPE)
        proc.check_returncode()
        out = proc.stdout.decode()

        monitors = []
        for monitor_config in cls._iter_monitor_configs(out):
            monitor = cls._from_raw(monitor_config)
            monitors.append(monitor)

        return monitors
