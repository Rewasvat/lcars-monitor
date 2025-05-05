#!/usr/bin/env python3
import os
import sys
import click
import libasvat.command_utils as cmd_utils
import libasvat.utils as utils
from lcarsmonitor.sensors.sensors import ComputerSystem
from lcarsmonitor.monitor import SystemMonitorApp
from lcarsmonitor.widgets.label import setup_lcars_fonts


class LCARSMonitorCommands(cmd_utils.RootCommands):
    """LCARS Monitor: monitor hardware sensors with a customizable LCARS-themed interface.

    While this is technically a CLI application and may have several CLI commands to perform different
    functions, the main use-scenario is using the `open` or `edit` commands to open our GUI.

    Check each sub-group/sub-command using `--help` for specific information on them.
    """

    def initialize(self):
        self.app_name = "lcarsmonitor"
        self.module_ignore_paths.append("main")
        super().initialize()
        setup_lcars_fonts()

    def get_default_standalone_args(self):
        return ["run"]

    @cmd_utils.instance_command()
    @click.option("--test", "-t", is_flag=True, help="Use dummy testing sensors")
    def run(self, test):
        """Runs the LCARS Monitor GUI.

        The GUI will be opened in the last mode used (EDIT or DISPLAY). It defaults to EDIT mode if it wasn't used before.
        This is the default command when running the application without any arguments.
        """
        self.open_gui(test_sensors=test)

    @cmd_utils.instance_command()
    @click.option("--test", "-t", is_flag=True, help="Use dummy testing sensors")
    @click.option("--system-name", "-s", type=str, default=None, help="Name of UISystem to force-select to display.")
    def open(self, test=False, system_name=None):
        """Opens the System Monitor GUI in DISPLAY mode.

        The displayed UISystem will be the one selected as the 'main' system in EDIT mode.
        However, if SYSTEM_NAME is given, that system will be displayed instead.
        """
        self.open_gui(force_edit_mode=False, force_system_name=system_name, test_sensors=test)

    @cmd_utils.instance_command()
    @click.option("--test", "-t", is_flag=True, help="Use dummy testing sensors")
    def edit(self, test):
        """Opens the System Monitor GUI in EDIT mode."""
        self.open_gui(force_edit_mode=True, test_sensors=test)

    def open_gui(self, force_edit_mode: bool = None, force_system_name: str = None, test_sensors=False):
        """Opens the System Monitor GUI with the given parameters.

        Args:
            force_edit_mode (bool, optional): Defaults to None. If not None, it will force the GUI to open in EDIT mode
                if True, or DISPLAY mode if False.
            force_system_name (str, optional): Defaults to None. If not None, it will force the GUI to open with the
                given UISystem name (only applies in DISPLAY mode).
            test_sensors (bool, optional): If True, the Monitor will only use dummy testing sensors instead of real ones.
                Real sensors will not be loaded, thus the available sensors will be quite limited, but the app will load/run
                much faster.
        """
        if test_sensors:
            ComputerSystem().open(True)
        elif not utils.is_admin_user():
            click.secho("Running System Monitor GUI without admin permissions!", fg="red")
            click.secho("Not all system sensors will be available or work properly.", fg="red")
        app = SystemMonitorApp(force_edit_mode, force_system_name)
        app.run()
        if app.do_restart:
            mode_name = "EDIT" if app.data.in_edit_mode else "DISPLAY"
            click.secho(f"Restarting the Monitor in {mode_name} mode...", fg="yellow")
            if utils.is_frozen():
                utils.try_app_restart()
            else:
                os.execl(sys.argv[0], sys.argv[0], "run")


root = LCARSMonitorCommands()
main = root.click_group

root.check_standalone_execution()
