import argparse
import logging
import os
import json
from .controller import NaimController

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

CONFIG_DIR = os.path.expanduser("~/.config/pynaim")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config() -> dict:
    """Load configuration from a JSON file."""
    #TODO: Handle empty config file correctly
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        return {}

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    """Save configuration to a JSON file."""
    #TODO: Save config on better suited location
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def build_parser() -> argparse.ArgumentParser:
    """Build a command line argument parser."""

    parser = argparse.ArgumentParser(
        prog="pynaim",
        description="Python CLI tool to control Naim Mu-so 2nd Generation",
        epilog="Enjoy using the Naim CLI! For more information, visit: https://github.com/blaauboer/pynaim",
    )

    parser.add_argument(
        "--host",
        help="Hostname or IP-address (e.g. 192.168.1.200) of the device.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=15081,
        help="Port (default: 15081)",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Config ---
    subparsers.add_parser("set_host", help="Set the default host.")

    # --- Power ---
    power = subparsers.add_parser("power", help="Control power state")
    power.add_argument(
        "action",
        choices=["on", "off"],
        nargs="?",
        default="on",
        help="Turn the device on or off (default: 'on').",
    )

    # --- Playback ---
    subparsers.add_parser("play", help="Start playback")
    subparsers.add_parser("pause", help="Pause playback")
    subparsers.add_parser("stop", help="Stop playback")
    subparsers.add_parser("playpause", help="Toggle play/pause")
    subparsers.add_parser("next", help="Next track")
    subparsers.add_parser("previous", help="Previous track")

    # Volume
    volume = subparsers.add_parser("volume", help="Control volume")
    volume_sub = volume.add_subparsers(dest="volume_cmd", required=True)

    volume_sub.add_parser("up", help="Increase volume")
    volume_sub.add_parser("down", help="Decrease volume")
    volume_sub.add_parser("mute", help="Mute volume")
    volume_sub.add_parser("unmute", help="Unmute volume")

    volume_level = volume_sub.add_parser("level", help="Set volume level (0-100)")
    volume_level.add_argument("value", type=int, help="Volume level (0-100)")

    return parser


def main():
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if args.verbosity:
        logging.basicConfig(level=logging.DEBUG)

    config = load_config()

    # Handle set_host separately
    if args.command == "set_host":
        config["host"] = args.host
        save_config(config)
        print(f"Default host set to {args.host}")
        return 0

    # Use provided host or fall back to saved host in config
    if args.host:
        config["host"] = args.host
        save_config(config)
    elif "host" in config:
        args.host = config["host"]
    else:
        parser.error("Host must be specified either via --host or in the config file.")

    controller = NaimController(host=args.host, port=args.port)

    # --- Power ---
    if args.command == "power":
        if args.action == "off":
            controller.turn_off()
            print("Turning off the device...")
        else:
            controller.turn_on()
            print("Turning on the device...")

    # --- Playback ---
    elif args.command == "play":
        controller.media_play()
        print("Playing media...")
    elif args.command == "pause":
        controller.media_pause()
        print("Media paused.")
    elif args.command == "stop":
        controller.media_stop()
        print("Media stopped.")
    elif args.command == "playpause":
        controller.media_play_pause()
        print("Toggled play/pause.")
    elif args.command == "next":
        controller.media_next_track()
        print("Skipped to next track.")
    elif args.command == "previous":
        controller.media_previous_track()
        print("Back to previous track.")

    # --- Volume ---
    elif args.command == "volume":
        if args.volume_cmd == "up":
            controller.volume_up()
            print("Volume increased.")
        elif args.volume_cmd == "down":
            controller.volume_down()
            print("Volume decreased.")
        elif args.volume_cmd == "mute":
            controller.volume_mute()
            print("Volume muted.")
        elif args.volume_cmd == "unmute":
            controller.volume_unmute()
            print("Volume unmuted.")
        elif args.volume_cmd == "level":
            if not (0 <= args.value <= 100):
                parser.error("Volume level must be between 0 and 100")
            if args.value > 30:
                print("Warning: Setting volume above 30% may be loud!")
            else:
                controller.volume_set(args.value)
                print(f"Volume set to {args.value}.")
        else:
            parser.error("Invalid volume command.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
