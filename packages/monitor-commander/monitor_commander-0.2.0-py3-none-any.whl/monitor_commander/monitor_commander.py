#! /usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import asyncio
import dataclasses
import os
import re
import sys
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter, RawTextHelpFormatter
from dataclasses import MISSING, dataclass, field, is_dataclass
from enum import Enum
from itertools import zip_longest
from pathlib import Path
from subprocess import PIPE, run
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Type, TypeVar, Union, get_args, get_origin

import typedload
import yaml
from argcomplete import autocomplete, split_line
from argcomplete.completers import ChoicesCompleter, FilesCompleter
from typedload.exceptions import TypedloadException

_RUNTIME_CONFIG_PATH = Path("/usr/local/share/monitor-commander.yml")
_CONFIG_ROOTS = (Path("/usr/local/etc/"), Path("/etc/"))
_T = TypeVar("_T")
_U = TypeVar("_U")


def print_err(*values: object, sep: Optional[str] = None, end: Optional[str] = None, flush: bool = False) -> None:
    print(*values, sep=sep, end=end, flush=flush, file=sys.stderr)


def _safe_cast(val: Any, to_type: Callable[[Any], _T], default: _U = None) -> Union[_T, _U]:
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


_MonitorProperties = Union[int, str]
_VcpValue = Union[int, str]


@dataclass
class _RuntimeConfig:
    frozen: Set[str] = field(default_factory=set)


@dataclass
class _ConfigMonitor:
    name: str = field(metadata={"doc": "Name of the monitor. Used with the --monitor argument"})
    selector: Dict[str, _MonitorProperties] = field(
        metadata={
            "doc": "Select the physical monitors. Monitor must match all the values to be a match",
            "subdocs": ["Use the 'monitors' action to see valid keys and values."],
        }
    )
    presets: Dict[str, Dict[str, _VcpValue]] = field(
        metadata={
            "doc": "Configurations a monitor can be set to",
            "subdocs": [
                "Name of the preset",
                "VCP key and value to be set. Use `ddcutil capabilities` and `ddcutil getvcp ALL` to get the correct keys and values",
            ],
        }
    )


@dataclass
class _Config:
    monitors: List[_ConfigMonitor] = field(
        metadata={
            "doc": "Configured monitors. Physical monitors are associated with the first match in the list. It is possible for multiple monitor to match the same config."
        }
    )
    ddcutil_options: List[str] = field(
        default_factory=list,
        metadata={"doc": "Extra arguments to pass when calling ddcutil"},
    )
    ddcutil_parallel: bool = field(
        default=True,
        metadata={
            "doc": "Execute calls to ddcutil in parallel. Can cause issues when multiple screens share a physical connection"
        },
    )


def _load_yaml(path: Path, return_type: Type[_T]) -> _T:
    with path.open(encoding="utf-8") as f:
        try:
            return typedload.load(yaml.safe_load(f), return_type, failonextra=True)  # type: ignore
        except TypedloadException as e:
            print_err(f"Error reading {path}:")
            print_err(e)
            sys.exit(1)


def _locate_config(path: Optional[str]):
    if path and os.path.isabs(path):
        return Path(path)
    if path and re.fullmatch("[A-Za-z0-9]+", path) is None:
        print_err("--config contains forbidden chars. Please provide an absolute path")
        sys.exit(2)

    filename = f"monitor-commander-{path}.yml" if path else "monitor-commander.yml"
    for folder in _CONFIG_ROOTS:
        file_path = folder / filename
        if file_path.exists():
            return file_path
    if path:
        print_err(f"Cannot find config file {filename}")
        sys.exit(3)

    print_err("No config file found. Please create one")
    return None


def _load_config(path: Optional[str]):
    config_file = _locate_config(path)
    if config_file:
        return _load_yaml(config_file, _Config)
    else:
        # Stub config. Allows using 'monitor-commander monitors' before creating the file
        return _Config(monitors=[])


def _load_runtime_config():
    path = _RUNTIME_CONFIG_PATH
    if path.exists():
        return _load_yaml(path, _RuntimeConfig)
    else:
        return _RuntimeConfig()


def _save_runtime_config(config: _RuntimeConfig):
    path = _RUNTIME_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(typedload.dump(config), f)  # type: ignore


def _ddcutil(config: _Config):
    return ["ddcutil", *config.ddcutil_options]


def _handle_display_line(properties: Dict[str, str], current_display: Dict[str, _MonitorProperties], line: str):
    line = line.strip()
    for prefix, key in properties.items():
        if line.startswith(prefix):
            value = line[len(prefix) :].strip()
            if key == "bus":
                value = int(value.rsplit("-", 1)[-1])
            elif key == "year":
                values = value.split(",")
                value = int(values[0])
                if len(values) > 1:
                    _handle_display_line(properties, current_display, values[1])
            elif key == "week":
                value = int(value)
            current_display[key] = value
            break


def _detect_monitors(config: _Config) -> List[Dict[str, _MonitorProperties]]:
    for i in range(2):
        if i != 0:
            print_err("retry...")
            sleep(1)
        proc = run([*_ddcutil(config), "detect", "--async", "--nousb"], stdout=PIPE, text=True, check=False)
        out = proc.stdout
        if proc.returncode != 0:
            print(out)
            print_err("ddcutil returned and error")
            continue

        displays: List[Dict[str, _MonitorProperties]] = []
        current_display: Optional[Dict[str, _MonitorProperties]] = None
        display_prefix = "Display "
        properties = {
            "I2C bus:": "bus",
            "Mfg id:": "manufacturer",
            "Model:": "model",
            "Serial number:": "serial_number",
            "Manufacture year:": "year",
            "EDID version:": "edid_version",
            "VCP version:": "vcp_version",
            "Product code:": "product_code",
            "Week:": "week",
        }
        for line in out.splitlines():
            if current_display:
                if line:
                    _handle_display_line(properties, current_display, line)
                else:
                    displays.append(current_display)
                    current_display = None
            elif line.startswith(display_prefix):
                number = _safe_cast(line[len(display_prefix)].strip(), int)
                if isinstance(number, int):
                    current_display = {"display": number}

        if displays:
            return displays

        print_err("No monitor found")
    return []


def _monitor_match(selector: Dict[str, _MonitorProperties], monitor: Dict[str, _MonitorProperties]):
    for key, value in selector.items():
        if monitor.get(key) != value:
            return False
    return True


def _get_vcp_requests(monitor: _ConfigMonitor, preset_name: str):
    preset_values = monitor.presets.get(preset_name)
    if preset_values:
        return list(preset_values.items())
    return None


SetVcp = Tuple[str, _VcpValue]


@dataclass
class VcpSet:
    name: str
    bus: str
    vcp: List[SetVcp]


def _get_vcp_command(vcp: Tuple[VcpSet, SetVcp], log_prefix: str = ""):
    print(f"{log_prefix}check {vcp[0].name}({vcp[0].bus}): {vcp[1][0]}={vcp[1][1]}")
    return ["--bus", vcp[0].bus, "--terse", "getvcp", str(vcp[1][0])]


def _set_vcp_command(vcp: Tuple[VcpSet, SetVcp], log_prefix: str, verify: bool):
    print(f"{log_prefix}set {vcp[0].name}({vcp[0].bus}): {vcp[1][0]}={vcp[1][1]}")
    extra = ["--verify"] if verify else []
    return ["--bus", vcp[0].bus, *extra, "setvcp", str(vcp[1][0]), str(vcp[1][1])]


async def _run_retry(command: Sequence[str], pipeout: bool = False, log_prefix: str = ""):
    rc = -1
    out = b""
    args = {}
    if pipeout:
        args["stdout"] = PIPE
    for i in range(2):
        if i != 0:
            print_err(f"{log_prefix}retry...")
        proc = await asyncio.create_subprocess_exec(*command, **args)
        out, _ = await proc.communicate()
        rc = proc.returncode
        print(f"{log_prefix}ret={rc}")
        if rc == 0:
            break
    return rc, out.decode("utf-8") if out else None


def _check_getvcp_out(out: str, vcp: SetVcp):
    parts = out.strip().split(" ")
    if parts[0] == "VCP":
        key = parts[1]
        if key != vcp[0]:
            print_err(f"[ERROR] wrong getvcp output. Expected key {key}: {out}")
            return False
        else:
            vcp_type = parts[2]
            value = None
            if vcp_type == "CNC":
                print_err("[ERROR] check is not supported for CNC values. Use --no-check to bypass.")
                return False
            if vcp_type == "C" and len(parts) == 5:
                value = parts[3]
            elif vcp_type == "SNC" and len(parts) == 4:
                value = parts[3]
            if value:
                if value[0] == "x":
                    value = "0" + value
                return value == str(vcp[1])

    print_err(f"[ERROR] cannot parse getvcp output: {out}")
    return False


_process_id = 0


def get_prefix():
    global _process_id
    _process_id += 1
    return f"[{_process_id}] "


async def _set_vcp(ddcutil: List[str], check: bool, verify: bool, *vcps: Tuple[VcpSet, SetVcp]):
    async def set_vcp(vcp: Tuple[VcpSet, SetVcp]):
        if check:
            log_prefix = get_prefix()
            command = [*ddcutil, *_get_vcp_command(vcp, log_prefix)]
            _, out = await _run_retry(command, log_prefix=log_prefix, pipeout=True)
            if _check_getvcp_out(out or "", vcp[1]):
                return True

        log_prefix = get_prefix()
        command = [*ddcutil, *_set_vcp_command(vcp, log_prefix, verify)]
        rc, _ = await _run_retry(command, log_prefix=log_prefix)
        return rc == 0

    await asyncio.gather(*[set_vcp(vcp) for vcp in vcps])


def _set_monitors(
    config: _Config,
    arg_monitor: Optional[str],
    arg_preset: str,
    check: bool,
    verify: bool,
):
    runtime_config = _load_runtime_config()

    to_set: List[VcpSet] = []
    for connected_monitor in _detect_monitors(config):
        for config_monitor in config.monitors:
            if _monitor_match(config_monitor.selector, connected_monitor):
                if arg_monitor and config_monitor.name != arg_monitor:
                    pass
                elif not arg_monitor and config_monitor.name in runtime_config.frozen:
                    print_err(f"Monitor {config_monitor.name} is frozen. Skiping")
                else:
                    reqs = _get_vcp_requests(config_monitor, arg_preset)
                    if reqs:
                        to_set.append(VcpSet(config_monitor.name, str(connected_monitor["bus"]), reqs))
                    else:
                        print_err(f"Monitor {config_monitor.name}: no config found for preset <{arg_preset}>")
                    break

    vcps = zip_longest(*map(lambda s: s.vcp, to_set))
    ddcutil = _ddcutil(config)
    for vcp in vcps:
        monitors = zip(to_set, vcp)
        if config.ddcutil_parallel:
            asyncio.run(_set_vcp(ddcutil, check, verify, *monitors))
        else:
            for monitor in monitors:
                asyncio.run(_set_vcp(ddcutil, check, verify, monitor))


def _action_freeze(config: _Config, monitor: Optional[str], freeze: bool):
    monitors = [monitor] if monitor else [monitor.name for monitor in config.monitors]

    runtime_config = _load_runtime_config()
    if freeze:
        runtime_config.frozen.update(monitors)
    else:
        runtime_config.frozen.difference_update(monitors)
    _save_runtime_config(runtime_config)
    _action_status()


def _action_status():
    runtime_config = _load_runtime_config()
    frozen = runtime_config.frozen
    if frozen:
        print("Frozen monitors:")
        for freeze in frozen:
            print(freeze)
    else:
        print("No frozen monitor")


def _action_monitors(config: _Config):
    connected_monitors = _detect_monitors(config)
    if not connected_monitors:
        print("No monitor found")
    for connected_monitor in connected_monitors:
        print("")
        for key, value in connected_monitor.items():
            print(f"{key}: {repr(value)}")
        for config_monitor in config.monitors:
            if _monitor_match(config_monitor.selector, connected_monitor):
                print(f"=> Matched configured monitor <{config_monitor.name}>")
                break
        else:
            print("=> No match in configured monitors")


def _elevate():
    print_err("Action require root privileges")
    command = ["sudo", sys.executable, *sys.argv]
    os.execvp(command[0], command)


def _ddcutil_need_root():
    for device in Path("/dev").glob("i2c-*"):
        if not os.access(device, os.W_OK, effective_ids=os.access in os.supports_effective_ids):
            return True
    return False


def _config_need_root(read_only: bool):
    access = os.R_OK if read_only else os.W_OK
    config = _RUNTIME_CONFIG_PATH
    while not config.exists():
        config = config.parent
    return not os.access(config, access, effective_ids=os.access in os.supports_effective_ids)


class ElevateType(Enum):
    DDCUTIL = 0
    READ_CONF = 1
    WRITE_CONF = 2


def _elevate_if_needed(elevate_type: ElevateType):
    if os.getuid() == 0:
        return

    if elevate_type == ElevateType.DDCUTIL:
        needroot = _ddcutil_need_root()
    elif elevate_type == ElevateType.READ_CONF:
        needroot = _config_need_root(True)
    elif elevate_type == ElevateType.WRITE_CONF:
        needroot = _config_need_root(False)

    if needroot:
        _elevate()


def _help_parse_type(type_class: Any):
    basic_types = (str, bool, int)
    type_str: str = ""
    type_origin = get_origin(type_class)
    type_dict: bool = type_origin == dict
    type_list: bool = type_origin == list
    type_union: bool = type_origin == Union  # pylint: disable=comparison-with-callable

    if type_list:
        type_class = get_args(type_class)[0]

    type_dataclass = is_dataclass(type_class)

    if type_class in basic_types:
        type_str = type_class.__name__
    elif type_union:
        subtypes = get_args(type_class)
        subtypes_str = [subtype.__name__ for subtype in subtypes if subtype in basic_types]
        if len(subtypes_str) == len(subtypes):
            type_str = " | ".join(subtypes_str)

    if type_str:
        if type_list:
            type_str = f"<List<{type_str}>>"
        else:
            type_str = f"<{type_str}>"

    return (
        type_str,
        type_class if type_dataclass else None,
        type_class if type_dict else None,
        type_list,
    )


def _help_handle_prefix(prefix_length: int, list_prefix: bool):
    if list_prefix:
        prefix = prefix_length * " " + "- "
        prefix_length += 2
    else:
        prefix = prefix_length * " "
    return prefix, prefix_length


def _help_line(
    prefix: str,
    key: str,
    type_str: str,
    doc: str,
    default: str,
):
    line = f"{prefix}{key}: "
    if type_str:
        line += type_str + " "
    if doc or default:
        line += "# "
        if doc:
            line += doc + " "
        if default:
            line += f"(default: {default})"

    return line


def _help_increment_prefix(prefix_length: int):
    return prefix_length + 2


def _get_help_dict(type_dict: Any, prefix_length: int, parent_list: bool, subdocs: List[str]):
    type_key, type_value = get_args(type_dict)
    type_key_str, type_dataclass, type_dict, type_list = _help_parse_type(type_key)
    if type_dataclass or type_dict or type_list:
        raise NotImplementedError("")
    type_value_str, type_dataclass, type_dict, type_list = _help_parse_type(type_value)
    doc = subdocs[0] if subdocs else ""
    prefix, prefix_length = _help_handle_prefix(prefix_length, parent_list)
    line = _help_line(prefix, type_key_str, type_value_str, doc, "")
    lines = [line]

    if type_dict:
        lines.extend(_get_help_dict(type_dict, _help_increment_prefix(prefix_length), type_list, subdocs[1:]))

    if type_dataclass:
        lines.extend(_get_help_dataclass(type_dataclass, _help_increment_prefix(prefix_length), type_list))
    return lines


def _get_help_dataclass(data_class: Any, prefix_length: int = 0, parent_list: bool = False):
    lines: List[str] = []
    first = True
    for dc_field in dataclasses.fields(data_class):
        key = dc_field.name
        doc = dc_field.metadata.get("doc", "")

        type_class = dc_field.type
        type_str, type_dataclass, type_dict, type_list = _help_parse_type(type_class)

        default_str = ""
        if dc_field.default != MISSING:
            default_str = str(dc_field.default)
        elif dc_field.default_factory == list:  # type: ignore # Typing bug: default_factory has wrong type
            default_str = "[]"
        elif dc_field.default_factory != MISSING:  # type: ignore # Typing bug: default_factory has wrong type:
            raise NotImplementedError("")

        prefix, prefix_length = _help_handle_prefix(prefix_length, first and parent_list)
        lines.append(_help_line(prefix, key, type_str, doc, default_str))
        if type_dict:
            lines.extend(
                _get_help_dict(
                    type_dict,
                    _help_increment_prefix(prefix_length),
                    type_list,
                    dc_field.metadata.get("subdocs", []),
                )
            )
        if type_dataclass:
            lines.extend(_get_help_dataclass(type_dataclass, _help_increment_prefix(prefix_length), type_list))
        first = False
    return lines


class HelpFormatter(RawTextHelpFormatter, RawDescriptionHelpFormatter):
    pass


def _get_argv():
    argv = sys.argv

    # When completing arguments, sys.argv will contain only the script name
    # We need to parse COMP_LINE to get the "real" arguments
    if "_ARGCOMPLETE" in os.environ and "COMP_LINE" in os.environ:
        _, _, _, argv, _ = split_line(os.environ["COMP_LINE"])

    return argv


def main():
    config_parser = ArgumentParser(add_help=False)
    argument = config_parser.add_argument(
        "--config",
        help=textwrap.dedent(
            f"""
                Configuration file to be used. Format is:
                ---
                {{format}}
                ---
                By default will search a file named monitor-commander.yml in folders {', '.join([p.as_posix() for p in _CONFIG_ROOTS])}.
                If value contain only letters and digits, it will search for file monitor-commander-<value>.yml instead.
                Else the value can be and absolute path to a file.
            """
        )
        .strip()
        .format(format="\n".join(_get_help_dataclass(_Config))),
    )
    setattr(argument, "completer", FilesCompleter)

    # We need to pre-parse the command line as other completions depend on the config file
    args, _ = config_parser.parse_known_args(_get_argv()[1:])
    config = _load_config(args.config)

    parser = ArgumentParser(parents=[config_parser], formatter_class=HelpFormatter)
    monitors = {monitor.name for monitor in config.monitors}
    monitor_argument = {
        "choices": monitors,
        "help": "Limit action to the provided monitor",
    }
    subparsers = parser.add_subparsers(dest="action", metavar="action", required=True)

    helptxt = "Probe connected monitors"
    subparser = subparsers.add_parser("monitors", help=helptxt, description=helptxt)

    helptxt = "Freeze one or multiple monitors. The monitor will not be set unless explicitly specified with the --monitor arg"
    subparser = subparsers.add_parser("freeze", help=helptxt, description=helptxt)
    subparser.add_argument("--monitor", **monitor_argument)

    helptxt = "Unfreeze one or multiple monitors"
    subparser = subparsers.add_parser("unfreeze", help=helptxt, description=helptxt)
    subparser.add_argument("--monitor", **monitor_argument)

    helptxt = "Show freeze status"
    subparser = subparsers.add_parser("status", help=helptxt, description=helptxt)

    helptxt = "Set monitor(s) to a specific config"
    subparser = subparsers.add_parser("set", help=helptxt, description=helptxt, formatter_class=HelpFormatter)
    subparser.add_argument("--monitor", **monitor_argument)
    subparser.add_argument(
        "--no-check",
        dest="check",
        action="store_false",
        help="Do not check values before setting them",
    )
    subparser.add_argument(
        "--no-verify",
        dest="verify",
        action="store_false",
        help="Do not verify values after setting them",
    )
    argument = subparser.add_argument(
        "preset",
        help=textwrap.dedent(
            """
                Name of the monitor(s) preset to apply.
                Value must be declared in the configuration file.
            """,
        ).strip(),
    )
    setattr(
        argument, "completer", ChoicesCompleter({preset for monitor in config.monitors for preset in monitor.presets})
    )

    autocomplete(parser)
    args = parser.parse_args()

    if args.action == "monitors":
        _elevate_if_needed(ElevateType.DDCUTIL)
        _action_monitors(config)
    elif args.action == "freeze":
        _elevate_if_needed(ElevateType.WRITE_CONF)
        _action_freeze(config, args.monitor, True)
    elif args.action == "unfreeze":
        _elevate_if_needed(ElevateType.WRITE_CONF)
        _action_freeze(config, args.monitor, False)
    elif args.action == "status":
        _elevate_if_needed(ElevateType.READ_CONF)
        _action_status()
    elif args.action == "set":
        _elevate_if_needed(ElevateType.DDCUTIL)
        _set_monitors(config, args.monitor, args.preset, args.check, args.verify)


if __name__ == "__main__":
    main()
