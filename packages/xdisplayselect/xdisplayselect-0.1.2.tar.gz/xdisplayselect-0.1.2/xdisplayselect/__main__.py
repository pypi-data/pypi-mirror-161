from typing import cast

from xdisplayselect.config import Config
from xdisplayselect.monitor import ConnectedMonitor, DisconnectedMonitor, Monitor
from xdisplayselect.monitor_config import MonitorConfig


def main(conf: Config) -> None:
    monitors = Monitor.get_xrandr_monitors()
    connected_monitors = cast(list[ConnectedMonitor], [mon for mon in monitors if mon.connected])
    disconnected_monitors = cast(list[DisconnectedMonitor], [mon for mon in monitors if not mon.connected])

    if conf.restore:
        try:
            print("Trying to obtain monitor configuration from cache")
            monitor_conf = MonitorConfig.load_config(connected_monitors, conf.cache_file)
        except ValueError:
            print("Unable to find this configuration in cache, prompting instead.")
            monitor_conf = MonitorConfig.prompt_for_setup(connected_monitors)
    else:
        print("Skipping cache restoring, prompting for monitor setup")
        monitor_conf = MonitorConfig.prompt_for_setup(connected_monitors)

    xargs_cmd = monitor_conf.cmd_args

    # Also explicitly mark other disconnected monitors as off
    for disconnected_mon in disconnected_monitors:
        xargs_cmd.extend(["--output", disconnected_mon.name, "--off"])

    print(f"Would run: {xargs_cmd}")


def cli() -> None:
    conf = Config.parse()
    main(conf)


if __name__ == "__main__":
    cli()
