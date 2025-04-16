#!/usr/bin/env python3
import click
import libasvat.command_utils as cmd_utils
import libasvat.utils as utils
import lcarsmonitor.sensors as sensors
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
        return ["edit"]

    @cmd_utils.instance_command()
    @click.option("--test", "-t", is_flag=True, help="Use dummy testing sensors")
    def open(self, test):
        """Opens the System Monitor GUI in DISPLAY mode."""
        if test:
            sensors.ComputerSystem().open(True)
        elif not utils.is_admin_user():
            click.secho("Can't run the System Monitor GUI without admin permissions!", fg="red")
            # return  # TODO: fix this
        app = SystemMonitorApp(False)
        app.run()

    @cmd_utils.instance_command()
    @click.option("--test", "-t", is_flag=True, help="Use dummy testing sensors")
    def edit(self, test):
        """Opens the System Monitor GUI in EDIT mode."""
        if test:
            sensors.ComputerSystem().open(True)
        elif not utils.is_admin_user():
            click.secho("Can't run the System Monitor GUI without admin permissions!", fg="red")
            # return
        app = SystemMonitorApp(True)
        app.run()


root = LCARSMonitorCommands()
main = root.click_group

root.check_standalone_execution()
