import asyncio
import httpx
import logging

from dataclasses import dataclass
from typing import Optional, Dict

DEFAULT_PORT = 15081
DEFAULT_VOLUME_STEP = 3

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__name__)


@dataclass
class NaimController:
    host: str
    port: int = DEFAULT_PORT

    volume_step: int = DEFAULT_VOLUME_STEP

    def _base(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _command(self, method: str, path: str, params: Optional[Dict[str, str]] = None):
        url = f"{self._base()}/{path.lstrip('/')}"
        try:
            response = httpx.request(method=method.upper(), url=url, params=params)
            response.raise_for_status()

        except httpx.HTTPError as exc:
            _LOGGER.error(f"HTTP Exception for {exc.request.url} - {exc}")
        if params is None:
            return response.json()

    # --- Event stream ---

    async def event_stream(self):
        # TODO: Handle errors, skip emtpy line and implement retry after disconnect.
        url = f"{self._base()}/notify"
        # async with httpx.AsyncClient() as client:
        #    async with client.stream("GET", url) as response:
        #        async for chunk in response.aiter_bytes():
        #           print(chunk)

        while True:
            try:
                async with httpx.AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_lines():
                            if chunk.strip():  # Skip empty lines
                                _LOGGER.debug(chunk)
            except (httpx.HTTPError, httpx.ConnectError) as exc:
                _LOGGER.error(f"Event stream error: {exc}. Retrying in 5 seconds...")
                await asyncio.sleep(5)

    # --- Power ---
    def turn_on(self):
        """Turn the media player on."""
        return self._command("PUT", "power", {"system": "on"})

    def turn_off(self):
        """Turn the media player off."""
        return self._command("PUT", "power", {"system": "lona"})

    # --- Playback ---
    def media_play(self):
        """Send play command."""
        return self._command("GET", "nowplaying", {"cmd": "play"})

    def media_pause(self):
        """Send play command."""
        return self._command("GET", "nowplaying", {"cmd": "pause"})

    def media_stop(self):
        """Send stop command."""
        return self._command("GET", "nowplaying", {"cmd": "stop"})

    def media_play_pause(self):
        """Send play/pause toggle command."""
        return self._command("GET", "nowplaying", {"cmd": "playpause"})

    def media_next_track(self):
        """Send next command."""
        return self._command("GET", "nowplaying", {"cmd": "next"})

    def media_previous_track(self):
        """Send previous media track command."""
        return self._command("GET", "nowplaying", {"cmd": "prev"})

    # --- Playback modes ---
    def set_repeat(self, repeat_mode: int):
        """Set repeat mode. Repeat mode: 0 = off, 1 = track, 2 = all."""
        if repeat_mode not in (0, 1, 2):
            raise ValueError("Invalid repeat mode. Use 0, 1, or 2.")
        return self._command("PUT", "levels/room", {"repeat": repeat_mode})

    # --- Volume ---
    def volume_up(self):
        """Send volume up command."""
        # TODO: transfer current_volume to a function.
        current_volume = int(httpx.get(f"{self._base()}/levels").json()["volume"])
        return self._command(
            "PUT", "levels", {"volume": current_volume + self.volume_step}
        )

    def volume_down(self):
        """Send volume down command."""
        # TODO: transfer current_volume to a function.
        current_volume = int(httpx.get(f"{self._base()}/levels").json()["volume"])
        return self._command(
            "PUT", "levels", {"volume": current_volume - self.volume_step}
        )

    def volume_set(self, volume: int):
        """Set volume level, range 0..100."""
        return self._command("PUT", "levels", {"volume": volume})

    def volume_mute(self):
        """Mute the volume."""
        return self._command("PUT", "levels", {"mute": 1})

    def volume_unmute(self):
        """Unmute the volume."""
        return self._command("PUT", "levels", {"mute": 0})

    # --- Source selection ---
    def select_source(self, source_path: str):
        """Select input source."""
        # TODO: Validate source_path against available and selectable inputs.
        return self._command("GET", f"inputs/{source_path.lower()}", {"cmd": "select"})

    # --- Queries ---
    def get_diagnostics(self):
        """Fetch playback information."""
        return self._command("GET", "diagnostics")

    def get_favourites(self):
        """Fetch favorites information."""
        return self._command("GET", "favorites")

    def get_levels(self):
        """Fetch volume information."""
        return self._command("GET", "levels")

    def get_inputs(self):
        """Fetch inputs information."""
        return self._command("GET", "inputs")

    def get_network(self):
        """Fetch network information."""
        return self._command("GET", "network")

    def get_now_playing(self):
        """Fetch playback information."""
        return self._command("GET", "nowplaying")

    def get_power(self):
        """Fetch power information."""
        return self._command("GET", "power")

    def get_update(self):
        """Fetch and return update information."""
        return self._command("GET", "update")

    # --- GET --- (Work in progress)
    def get_artist(self):
        """Return artist name of the currently playing track."""
        return self.get_now_playing()["artistName"]

    def get_title(self):
        """Return title of the currently playing track."""
        return self.get_now_playing()["title"]

    def get_album(self):
        """Return album name."""
        return self.get_now_playing()["albumName"]

    def get_artwork(self):
        """Return artwork URL."""
        return self.get_now_playing().get("artwork", {}).get("url", "")

    def get_selectable_inputs(self):
        """Return a list of available inputs."""
        data = self.get_inputs()
        children = data.get("children", [])
        return [child["name"] for child in children if child.get("selectable") == "1"]
