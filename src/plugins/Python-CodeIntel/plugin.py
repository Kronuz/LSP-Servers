import sublime

import os
import shutil

from SublimeCodeIntel.plugin.core.settings import ClientConfig
from SublimeCodeIntel.plugin.core.handlers import LanguageHandler
from SublimeCodeIntel.plugin.core.spinner import spinner

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def python_command():
    return "python3"


def python_is_installed():
    return shutil.which(python_command()) is not None


class CodeIntelPythonClientConfig(ClientConfig):
    def __init__(self):
        self.name = "python"
        self.binary_args = [
            python_command(),
            os.path.join(server_path, "pyls.py"),
            "-v",
            "--log-file",
            "~/.codeintel/pyls.log",
        ]
        self.tcp_port = None
        self.languages = {
            "python": {
                "scopes": ["source.python"],
                "syntaxes": ["python"],
            },
        }
        self.enabled = True
        self.init_options = {}
        self.settings = {
            "pyls": {
                "configurationSources": [
                    "flake8"
                ],
                "extraSysPath": [],
            },
        }
        self.env = {}

    def get_settings(self, window):
        pyls = dict(self.settings.get("pyls", {}))
        extraSysPath = pyls["extraSysPath"] = list(pyls.get("extraSysPath", []))
        extraSysPath.append(os.path.dirname(sublime.executable_path()))
        packages = window.extract_variables().get("packages")
        if packages and packages not in extraSysPath:
            extraSysPath.append(packages)
        for folder in window.folders():
            if folder not in extraSysPath:
                extraSysPath.append(folder)
        return {
            "pyls": pyls
        }


class CodeIntelPythonPlugin(LanguageHandler):
    def __init__(self):
        self._server_name = "Python Language Server"
        self._config = CodeIntelPythonClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not python_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(python_command()), self._server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        client.on_notification("textDocument/publishDiagnostics", self.on_diagnostics)

    def on_diagnostics(self, params):
        spinner.start("Python-CodeIntel", spinner='monkey')


def plugin_loaded():
    if not python_is_installed():
        sublime.message_dialog(
            "Please install Python 3")
