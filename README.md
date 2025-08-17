# pynaim

`pynaim` is a Python library and CLI tool to control Naim Uniti and Mu-so audio devices via their HTTP API. It provides methods for power control, playback, volume adjustment, source selection, and fetching device information.

The package is tested on an Naim Mu-so 2nd Generation, but should also work on at least some Uniti products. If you run into problems, please let me know.

---

## Features

- Power control: turn the device on/off
- Playback control: play, pause, stop, next/previous track, play/pause toggle
- Volume control: set, increase, decrease, mute, unmute
- Source selection: choose input source
- Query device information: diagnostics, favorites, network, now playing, volume levels, power state
- Asynchronous event stream support for real-time notifications (work in progress)
- Command-line interface (CLI) for quick control from terminal

---

## Installation

Install via PyPI:

```bash
pip install pynaim
```

---

## Usage in Python

```python
import asyncio
from pynaim import NaimController

controller = NaimController(host="192.168.1.100")
controller.turn_on()
controller.media_play()
controller.volume_up()
print(controller.get_now_playing())
```

---

## CLI Usage

Once installed, you can use the `pynaim` CLI:

```bash
# Set default host
pynaim set_host --host 192.168.1.100

# Power control
pynaim power on
pynaim power off

# Playback control
pynaim play
pynaim pause
pynaim stop
pynaim playpause
pynaim next
pynaim previous

# Volume control
pynaim volume up
pynaim volume down
pynaim volume mute
pynaim volume unmute
pynaim volume level 25
```

> Use `--verbosity` flag for more detailed logging.

---

## Event Stream

```python
async def main():
    controller = NaimController(host="192.168.1.100")
    await controller.event_stream()

asyncio.run(main())
```

> ⚠️ Event stream implementation is in progress; it handles reconnects but requires improved error handling.

---

## Methods

### Power
- `turn_on()`
- `turn_off()`
- `get_power()`

### Playback
- `media_play()`
- `media_pause()`
- `media_stop()`
- `media_play_pause()`
- `media_next_track()`
- `media_previous_track()`
- `get_now_playing()`
- `get_artist()`
- `get_title()`
- `get_album()`
- `get_artwork()`

### Volume
- `volume_up()`
- `volume_down()`
- `volume_set(volume: int)`
- `volume_mute()`
- `volume_unmute()`
- `get_levels()`

### Inputs / Sources
- `select_source(source_path: str)`
- `get_inputs()`
- `get_selectable_inputs()`

### Device Info
- `get_diagnostics()`
- `get_favourites()`
- `get_network()`
- `get_update()`

---

## Logging

`pynaim` uses Python's built-in `logging` module. Default level is `INFO`, HTTPX logs are set to `WARNING`.

```python
import logging
logging.basicConfig(level=logging.INFO)
```

---

## Notes
- Some methods use synchronous HTTP requests (`httpx.request`) for simplicity.
- Event streaming is asynchronous and requires `asyncio`.
- Volume up/down fetches current volume; future updates may cache the value.
- Source selection does not currently validate against available inputs.
- CLI stores default host in `~/.config/pynaim/config.json`.

---

## License

MIT License

