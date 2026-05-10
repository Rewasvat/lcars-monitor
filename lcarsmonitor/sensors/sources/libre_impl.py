##################################
# Sensor API implementation for LIBRE HARDWARE MONITOR LIB!
# See https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
###
# This expects the user to have the LHM app/Lib in their systems, and point LCARS Monitor
# to find and use it.
##################################
import os
import clr
import math
import click
import asyncio
import tempfile
import zipfile
import shutil
import requests
import threading
import traceback
import libasvat.imgui.editors.primitives as primitives
from typing import NamedTuple
from collections import deque
from datetime import datetime
from concurrent.futures import Future
from imgui_bundle import imgui, imgui_md # type: ignore
from libasvat.version import Version
from libasvat.imgui.math import Vector2
from libasvat.imgui.colors import Colors
from libasvat.imgui.popups import generic_button_with_popup
from lcarsmonitor.sensors.sensors_api import SensorSource, SensorID, HardwareType, SensorType, Hardware, InternalSensor


class LibreUpdateInfo(NamedTuple):
    """Information about LibreHardwareMonitor availability and updates.

    Returned by check_for_updates() to provide comprehensive version and update information.
    """

    has_update: bool
    """True if a newer version exists on GitHub than the locally installed version."""
    local_version: Version | None
    """The Version object of the locally installed LibreHardwareMonitor library, or None if not installed."""
    local_date: datetime | None
    """Creation/modification datetime of the local DLL file, or None if not available."""
    latest_version: Version | None
    """The latest Version available on GitHub, or None if unable to fetch from GitHub."""
    latest_date: datetime | None
    """Publication datetime of the latest GitHub release, or None if unable to fetch."""
    release_name: str | None
    """Name/title of the latest GitHub release, or None if unable to fetch."""
    release_notes: str | None
    """Full release notes/changelog from the latest GitHub release, or None if unable to fetch."""

    @property
    def local_timestamp(self):
        """Human-readable representation of our local_date attribute."""
        if self.local_date:
            return f"{self.local_date:%H:%M %d/%b/%Y}"
        return "N/A"

    @property
    def latest_timestamp(self):
        """Human-readable representation of our latest_date attribute."""
        if self.latest_date:
            return f"{self.latest_date:%H:%M %d/%b/%Y}"
        return "N/A"


class LibreComputer(SensorSource):
    """LCARSMonitor Sensor Source implementation using Libre Hardware Monitor.

    LibreHardwareMonitor (LHM for short), from https://github.com/LibreHardwareMonitor/LibreHardwareMonitor, is free
    software that can monitor the temperature sensors, fan speeds, voltages, load and clock speeds of your computer.

    LHM itself is a simple UI program on top of the Libre Hardware Monitor Lib (LHML), which is the actual library that
    allows monitoring computer sensors. This SensorSource uses the LHML from a local install of LHM in your machine to
    provide hardware/sensor data to LCARSMonitor.
    """

    def __init__(self):
        super().__init__()
        self._pretty_name = "Libre Hardware Monitor"
        self._pc = None
        self._lhm_path: str = None
        self._lhm_loaded = False
        self._last_message: str = "Please set the `library_path` property to a valid value"
        self._tried_loading_path: bool = False
        self._disable_auto_load: bool = True

        # Download progress tracking (0.0 to 1.0)
        self.download_progress: float = 0.0
        self._download_task: Future | None = None
        self._download_cancelled = False
        self._download_thread: threading.Thread = None
        self._download_temp_paths: list[str] = []

        # Message queue for UI display (stores up to 20 recent messages with timestamps)
        self.messages: deque = deque(maxlen=20)
        self._last_update_info: LibreUpdateInfo = None

    @primitives.string_property(is_folder=True)
    def library_path(self) -> str:
        """Path to LibreHardwareMonitor folder [GET/SET].

        The LibreHardwareMonitor (LHM) folder should contain the LibreHardwareMonitorLib.dll file which we'll load
        to access sensor data. As such, this property needs to be correctly set in order for this Sensor Source to work.

        To load the dll, other related DLLs should be in the same folder, so we need to point to the LHM folder directly.
        Usually when downloading the LHM release from GitHub, the ZIP contains a folder with all DLLs and more.

        When this property is set (in imgui - through select-folder dialog), we'll check the given path and try to load the LHMLib
        DLL. Any errors will be shown in the UI.

        However, if loading is successful, changing this property, for example to change which version of LHM you're using,
        WILL NOT CHANGE THE DLL THAT IS LOADED. The .NET framework does not allow unloading assemblies. The path will still
        be changed (and persisted!), but you'll need to restart this application entirely in order to "re-load" a different
        LHM DLL.
        """
        return self._lhm_path

    @library_path.setter
    def library_path(self, value: str):
        # NOTE: SensorSource base class handles loading/saving data from imgui-properties like this one.
        if value != self._lhm_path:
            self._lhm_path = value
            if not self._lhm_loaded:
                if not self._disable_auto_load:
                    self._load_lhm()
                else:
                    self._last_message = "DLL auto-load is disabled. Enable that or manually load the DLL."
            else:
                self._last_message = "Restart app to re-load DLL after path change (see tooltip). Previous DLL is loaded."

    @primitives.bool_property()
    def disable_auto_load(self) -> bool:
        """If checked, the LHM Lib DLL will NOT be auto-loaded by this SensorSource.

        If the DLL is not auto-loaded, the user will need to manually load it (using the `Load DLL` button in settings menu), or
        re-enable auto-loading. If the DLL is not loaded for whatever reason, this SensorSource will not be available.

        Auto-loading is great for user-experience since the user will not need to do anything for the SensorSource to work.
        However, if the DLL is loaded we cannot download/update the LHM files. Therefore disabling auto-loading is required for
        the LHM Update feature to work, afterwards auto-loading may be re-enabled until you need to update LHM again.
        """
        return self._disable_auto_load

    @disable_auto_load.setter
    def disable_auto_load(self, value: bool):
        self._disable_auto_load = value

    def check_availability(self):
        if (not self._tried_loading_path) and (not self._disable_auto_load):
            self._load_lhm()
        return self._lhm_loaded, self._last_message

    def _load_lhm(self):
        """Loads the LibreHardwareMonitorLib.dll from C#/.NET using the `clr` module.

        Appropriately updates our loaded/message attributes according to the result of loading the DLL.
        """
        if self._lhm_loaded:
            click.secho("[LibreSensors] Tried to re-load LHML DLL. Restart the app to be able to load a different DLL", fg="yellow")
            return

        self._tried_loading_path = True
        dll_name = "LibreHardwareMonitorLib.dll"
        dll_path = os.path.join(self.library_path, dll_name)
        if not os.path.isfile(dll_path):
            self._last_message = f"{dll_name} not found. Path '{self.library_path}' doesn't point to a valid LHM install"
            return

        try:
            # Load LibreHardwareMonitorLib (LHML) from C# .NET
            from System.Reflection import Assembly  # type: ignore
            Assembly.UnsafeLoadFrom(dll_path)
        except Exception as e:
            self._last_message = f"Error while loading {dll_name}: {e}"
            return

        self._lhm_loaded = True
        self._last_message = f"{dll_name} successfully loaded"

    def initialize(self):
        if not self._lhm_loaded:
            raise RuntimeError("Can't initialize LibreHardwareMonitor sensors without loading the LHM Lib.")

        from LibreHardwareMonitor.Hardware import Computer  # type: ignore

        # Initialize LHML Computer object
        self._pc = Computer()
        self._pc.IsCpuEnabled = True
        self._pc.IsGpuEnabled = True
        self._pc.IsMemoryEnabled = True
        self._pc.IsMotherboardEnabled = True
        self._pc.IsStorageEnabled = True
        self._pc.IsNetworkEnabled = True
        self._pc.IsBatteryEnabled = True
        self._pc.IsControllerEnabled = True
        self._pc.IsPsuEnabled = True
        self._pc.Open()

        for hw in self._pc.Hardware:
            self._hardwares.append(LibreHardware(hw))

    def shutdown(self):
        if self._pc is not None:
            self._pc.Close()
        # Cancel any pending download task
        self._cancel_download()
        super().shutdown()

    def _render_changelog_popup_contents(self):
        """Renders contents of our LHM CHANGELOG popup using imgui."""
        imgui_md.render(self._last_update_info.release_notes)
        imgui.separator()
        imgui.text("NOTE: this changelog is relative to the previous version.")
        imgui.text("There might be missing info in the changelog if your current version is older than the previous version.")
        if imgui.button("Close"):
            imgui.close_current_popup()

    def render_editor(self):
        super().render_editor()

        imgui.separator()
        if imgui.button("Refresh LHM Info from GitHub"):
            self.check_for_updates()
        if self._last_update_info:
            imgui.bullet_text(f"Current Version: {self._last_update_info.local_version} ({self._last_update_info.local_timestamp})")
            imgui.bullet_text(f"Latest  Version: {self._last_update_info.latest_version} ({self._last_update_info.latest_timestamp})")
            if self._last_update_info.release_notes:
                imgui.same_line()
                title = f"LibreHardwareMonitor {self._last_update_info.latest_version} CHANGELOG"
                size = Vector2(imgui.get_main_viewport().size)
                size.y -= imgui.get_text_line_height_with_spacing() * 3
                generic_button_with_popup("Open CHANGELOG", title, self._render_changelog_popup_contents, size*(0.85,0.85))
            # imgui.bullet_text(f"Latest Version Name: {self._last_update_info.release_name}")
            if self._last_update_info.has_update:
                imgui.text_colored(Colors.cyan, "UPDATE AVAILABLE!")
                if self._download_task:
                    if self._download_task.done():
                        # Download completed or not started
                        self._cancel_download()
                        self.check_for_updates()  # To update the local version
                    else:
                        imgui.text(f"Downloading LibreHardwareMonitor {self._last_update_info.release_name}")
                        imgui.progress_bar(self.download_progress)
                else:
                    if imgui.button("UPDATE"):
                        self.start_download_lib()
        else:
            imgui.text_colored(Colors.red, "Refresh data to check for updates.")

        if imgui.tree_node("Messages"):
            if len(self.messages) > 0:
                for color, msg in self.messages:
                    imgui.bullet()
                    imgui.same_line()
                    imgui.text_colored(color, msg)
            else:
                imgui.bullet_text("No messages to display...")
            imgui.tree_pop()

    def _add_message(self, text: str, fg: str = "white"):
        """Add a message to the message queue and print to console.

        Messages are stored with timestamps for UI display.
        Stores up to 20 recent messages.
        """
        msg = f"{text}"
        color = getattr(Colors, fg, Colors.white)
        self.messages.append((color, msg))
        click.secho(f"[LibreSensors] {msg}", fg=fg)

    def _get_dll_version(self, dll_path: str) -> str | None:
        """Extract version information from a Windows DLL file.

        Reads the PE (Portable Executable) header to extract the version string.
        Returns version as a string (e.g., "1.14.0") or None if version cannot be read.

        The method we use to get the DLL version depends on .NET Framework System.Diagnostics.FileVersionInfo
        """
        try:
            from System.Diagnostics import FileVersionInfo  # type: ignore
            file_info = FileVersionInfo.GetVersionInfo(dll_path)
            return file_info.FileVersion
        except Exception as e:
            self._add_message(f"Error while getting LHM DLL version: {e}", "red")
            return None

    def get_local_version(self) -> tuple[Version, datetime] | None:
        """Get the version and creation date of the locally installed LibreHardwareMonitor library.

        Reads version information from the LibreHardwareMonitorLib.dll file.
        Returns a tuple (Version, datetime) or None if not available.

        The Version object can be compared directly with other Version objects.
        The datetime is the file creation timestamp.
        """
        if not self._lhm_path:
            return None

        dll_path = os.path.join(self._lhm_path, "LibreHardwareMonitorLib.dll")
        if not os.path.isfile(dll_path):
            return None

        version_str = self._get_dll_version(dll_path)
        if not version_str:
            return None

        try:
            # Get file creation time
            timestamp = os.path.getctime(dll_path)
            file_datetime = datetime.fromtimestamp(timestamp)

            # Parse version string to Version object
            version = Version.from_string(version_str)

            return (version, file_datetime)
        except (OSError, ValueError) as e:
            self._add_message(f"Error parsing local LibreHardwareMonitor version/date: {e}", fg="red")
            return None

    async def _fetch_github_latest_release(self) -> dict | None:
        """Fetch the latest release information from LibreHardwareMonitor GitHub repository.

        Returns a dictionary with keys:
            - 'tag_name': version tag (e.g., 'v1.14.0')
            - 'name': release name
            - 'body': release notes
            - 'download_url': URL to the .zip asset
            - 'published_at': ISO timestamp string when release was published

        Returns None if fetch fails.
        """
        try:
            # Using GitHub API v3
            api_url = "https://api.github.com/repos/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest"

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(api_url, timeout=10)
            )
            response.raise_for_status()

            release_data = response.json()

            # Find the .zip asset - prioritize "LibreHardwareMonitor.zip", fall back to any .zip
            download_url = None
            for asset in release_data.get('assets', []):
                if asset['name'] == "LibreHardwareMonitor.zip":
                    download_url = asset['browser_download_url']
                    break

            # Fall back to any .zip file if specific one not found
            if not download_url:
                for asset in release_data.get('assets', []):
                    if asset['name'].endswith('.zip'):
                        download_url = asset['browser_download_url']
                        break

            if not download_url:
                return None

            return {
                'tag_name': release_data.get('tag_name', 'unknown'),
                'name': release_data.get('name', ''),
                'body': release_data.get('body', ''),
                'download_url': download_url,
                'published_at': release_data.get('published_at', None)
            }
        except Exception as e:
            self._add_message(f"Error fetching GitHub release: {e}", fg="red")
            return None

    def check_for_updates(self) -> LibreUpdateInfo:
        """Check if there's a newer version of LibreHardwareMonitor available.

        Queries the GitHub repository for the latest release and compares it with the locally installed version.
        Returns a LibreUpdateInfo object containing version information, timestamps, and release notes.
        """
        try:
            # Get local version
            local_info = self.get_local_version()
            local_version = None
            local_date = None
            if local_info:
                local_version, local_date = local_info

            # Fetch latest release info (synchronously via thread pool)
            import concurrent.futures
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                release_info = loop.run_until_complete(self._fetch_github_latest_release())
            finally:
                loop.close()

            if not release_info:
                self._last_update_info = LibreUpdateInfo(False, local_version, local_date, None, None, None, None)
                return self._last_update_info

            latest_tag = release_info['tag_name']
            # Remove 'v' prefix if present for version comparison
            latest_version_str = latest_tag.lstrip('v')

            try:
                latest_version = Version.from_string(latest_version_str)
            except (ValueError, AttributeError):
                self._last_update_info = LibreUpdateInfo(False, local_version, local_date, None, None, None, None)
                return self._last_update_info

            # Parse published_at timestamp
            latest_date = None
            if release_info.get('published_at'):
                try:
                    # Parse ISO format timestamp
                    latest_date = datetime.fromisoformat(release_info['published_at'].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass

            # Compare versions using Version object comparison
            has_update = False
            if latest_version:
                if local_version:
                    has_update = latest_version > local_version
                else:
                    has_update = True

            self._last_update_info = LibreUpdateInfo(
                has_update,
                local_version,
                local_date,
                latest_version,
                latest_date,
                release_info['name'],
                release_info['body']
            )
        except Exception as e:
            self._add_message(f"Error checking for updates: {e}", fg="red")
            self._last_update_info = LibreUpdateInfo(False, None, None, None, None, None, None)
        return self._last_update_info

    def start_download_lib(self) -> asyncio.Task | None:
        """Start an asynchronous download of the latest LibreHardwareMonitor release.

        This method creates and returns an asyncio Task that will download the latest
        release from GitHub, extract it to library_path, and preserve the config file.

        The download_progress attribute will be updated during download (0.0 to 1.0).
        Status messages will be added to the messages queue for UI display.

        Call this method to initiate the download, then check download_progress each frame
        from your UI code. The task can be awaited or checked with task.done().

        Returns the concurrent Future for the download operation, or None if library_path is invalid.
        """
        if not self._lhm_path or not os.path.isdir(self._lhm_path):
            self._add_message("library_path not set or invalid", fg="red")
            return None

        if self._download_task and self._download_task.running():
            return self._download_task

        if self._lhm_loaded:
            self._add_message("Cannot download & update LHM while it is loaded. Disable LHM and restart LCARSMonitor.", fg="yellow")
            return None

        # Reset state
        self._cancel_download()
        self.download_progress = 0.0
        self._download_cancelled = False
        self._download_temp_paths.clear()

        # Criamos a thread manualmente já marcada como daemon
        self._download_task = Future()
        self._download_thread = threading.Thread(target=self._download_thread_worker, args=(self._download_task,), daemon=True)
        self._download_thread.start()
        return self._download_task

    def _download_thread_worker(self, future: Future):
        """Method executed by our worker download-thread."""
        try:
            asyncio.run(self._download_lib_task())
        except Exception as e:
            # future.set_exception(e)
            click.secho(traceback.format_exc(e), fg="red")
            self._add_message(f"Error in Download Thread: {e}", "red")
        future.set_result("finished")

    def _cancel_download(self):
        """Cancels the currently running LHM download task, if any. Releases thread and other resources used for the download task."""
        self.download_cancelled = True
        if self._download_thread and self._download_thread.is_alive():
            self._download_thread.join()
        self._download_thread = None
        self._download_task = None

    async def _download_lib_task(self):
        """Internal async task for downloading and extracting LibreHardwareMonitor."""
        try:
            self.download_progress = 0.0

            # Fetch release info
            release_info = await self._fetch_github_latest_release()
            if not release_info:
                self._add_message("Failed to fetch latest release info", fg="red")
                self.download_progress = 0.0
                return

            self.download_progress = 0.1
            if self._download_cancelled:
                return

            # Download the zip file
            download_url = release_info['download_url']
            await self._download_and_extract_release(download_url)

            self.download_progress = 1.0
            self._add_message("LibreHardwareMonitor successfully downloaded and extracted", fg="green")

        except asyncio.CancelledError:
            self._add_message("Download cancelled", fg="yellow")
            self.download_progress = 0.0
        except Exception as e:
            click.secho(traceback.format_exc(e), fg="red")
            self._add_message(f"Download error: {e}", fg="red")
            self.download_progress = 0.0
        finally:
            # Cleanup temporary files
            for temp_path in self._download_temp_paths:
                if os.path.isfile(temp_path):
                    os.remove(temp_path)
                elif os.path.isdir(temp_path):
                    shutil.rmtree(temp_path)

    async def _download_and_extract_release(self, download_url: str):
        """Download and extract the LibreHardwareMonitor release zip file.

        Preserves the LibreHardwareMonitor.config file during extraction.
        Updates download_progress during the process.
        """
        loop = asyncio.get_event_loop()

        self.download_progress = 0.15
        if self._download_cancelled:
            return

        # Download the zip file
        zip_path = os.path.join(tempfile.gettempdir(), "LibreHardwareMonitor.zip")
        self._download_temp_paths.append(zip_path)

        response = await loop.run_in_executor(
            None,
            lambda: requests.get(download_url, stream=True, timeout=30)
        )
        response.raise_for_status()

        # Get total file size for progress calculation
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        # Write downloaded content
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if self._download_cancelled:
                    return

                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # Update progress: 15% -> 85%
                    if total_size > 0:
                        self.download_progress = 0.15 + (0.7 * (downloaded_size / total_size))

                    # Yield control to allow UI updates
                    await asyncio.sleep(0)

        self.download_progress = 0.85
        if self._download_cancelled:
            return

        # Extract zip to library_path
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the root folder in the zip (usually LibreHardwareMonitor-xxx)
            name_list = zip_ref.namelist()
            if not name_list:
                raise ValueError("Zip file is empty")

            # Find the root directory
            root_dir = name_list[0].split('/')[0]

            # Create temporary extraction folder
            temp_extract = os.path.join(tempfile.gettempdir(), "lhm_extract")
            self._download_temp_paths.append(temp_extract)
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)

            # Extract all files
            await loop.run_in_executor(None, zip_ref.extractall, temp_extract)
            # print(os.listdir(temp_extract))

        self.download_progress = 0.90
        if self._download_cancelled:
            return

        # Clear library_path (except config file)
        for item in os.listdir(self._lhm_path):
            item_path = os.path.join(self._lhm_path, item)
            if item != "LibreHardwareMonitor.config":
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        # Copy extracted files from root_dir to library_path
        source_dir = temp_extract  # os.path.join(temp_extract, root_dir)
        for item in os.listdir(source_dir):
            src_path = os.path.join(source_dir, item)
            dst_path = os.path.join(self._lhm_path, item)
            # print(f"Copying '{src_path}'->'{dst_path}' (file={os.path.isfile(src_path)})")

            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

        self.download_progress = 0.95
        if self._download_cancelled:
            return

        self.download_progress = 1.0
        # NOTE: no TRY/CATCH blocks in this method since we're executed by _download_lib_task(), and that method
        #   handles all exceptions we may rase, and also handles cleaning up any temp files we created.


class LibreHardware(Hardware):
    # Wraps and builds upon ``LibreHardwareMonitorLib.Hardware.IHardware`` interface.

    def __init__(self, hw, parent: 'LibreHardware' = None):
        """hw should be LHML's IHardware object"""
        isensors = [LibreSensor(self, s) for s in hw.Sensors]
        children = [LibreHardware(subhw, self) for subhw in hw.SubHardware]

        super().__init__(parent, isensors, children)
        self._hw = hw
        """Internal IHardware object from native C#"""
        self._type: HardwareType = None

    @property
    def id(self):
        return str(self._hw.Identifier)

    @property
    def name(self):
        return str(self._hw.Name)

    @property
    def type(self):
        if self._type is None:
            self._type = HardwareType.from_obj(self._hw.HardwareType)
        return self._type

    def update(self):
        if self.enabled:
            self._hw.Update()
            return super().update()


class LibreSensor(InternalSensor):
    """Represents a single ISensor object from C# for a hardware device.

    This is a simple wrapper of ``LibreHardwareMonitorLib.Hardware.ISensor`` interface, providing some basic identification values.

    A LibreComputer will always create all of its InternalSensors objects upon loading. Since we contain native C# objects, this class
    can't be pickled.

    A InternalSensor contains refs to all ``Sensor`` objects that use it. The ``Sensor`` class is the proper API to access/use sensor
    data, and it uses its InternalSensor object internally to access the underlying data.
    """

    def __init__(self, parent_hw, internal_sensor):
        """internal_sensor should be LHML's ISensor object"""
        super().__init__(parent_hw)
        self.isensor = internal_sensor  # LibreHardwareMonitor.Hardware.ISensor
        """Internal, fixed, ISensor object from LibreHardwareMonitor to access sensor data."""
        self._type: SensorType = None

    @property
    def id(self):
        return SensorID(self.isensor.Identifier)

    @property
    def name(self):
        return str(self.isensor.Name)

    @property
    def type(self):
        if self._type is None:
            self._type = SensorType.from_obj(self.isensor.SensorType)
        return self._type

    @property
    def limits(self):
        low = getattr(self.isensor, "LowLimit", None)
        high = getattr(self.isensor, "HighLimit", None)
        if low is not None and high is not None:
            return Vector2(low, high)

    @property
    def value(self):
        if self.isensor.Value:
            return float(self.isensor.Value)

    @property
    def value_range(self):
        minimum = self.isensor.Min or math.inf
        maximum = self.isensor.Max or -math.inf
        return Vector2(minimum, maximum)
