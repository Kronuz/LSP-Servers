import sublime

import os
import shutil

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def python_command():
    return "python3"


def python_is_installed():
    return shutil.which(python_command()) is not None


server_name = "Python Language Server"


class PythonClientConfig(ClientConfig):
    def __init__(self):
        self.name = "python"
        self.binary_args = [
            python_command(),
            os.path.join(server_path, "pyls.py"),
            "-v",
            "--log-file",
            "~/.lsp/pyls.log"
        ]
        self.tcp_port = None
        self.scopes = ["source.python"]
        self.syntaxes = ["python"]
        self.languageId = "python"
        self.enabled = True
        self.init_options = {}
        self.settings = {
            "pyls": {
                "configurationSources": [
                    "flake8"
                ],
                "extraSysPath": []
            }
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

    def get_language_id(self, view):
        return self.languageId


class LspPythonPlugin(LanguageHandler):
    def __init__(self):
        self._config = PythonClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not python_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(node_command()), server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        pass  # extra initialization here.


def plugin_loaded():
    if not python_is_installed():
        sublime.message_dialog(
            "Please install Python 3")
