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
default_name = "python"
default_config = ClientConfig(
    name=default_name,
    binary_args=[
        python_command(),
        os.path.join(server_path, "pyls.py"),
        "-v",
        "--log-file",
        "~/.lsp/pyls.log"
    ],
    tcp_port=None,
    scopes=["source.python"],
    syntaxes=["python"],
    languageId="python",
    enabled=True,
    init_options={},
    settings={
        "pyls": {
            "configurationSources": [
                "flake8"
            ],
            "extraSysPath": [
                "/Applications/Sublime Text.app/Contents/MacOS",
                os.path.expanduser("~/Library/Application Support/Sublime Text 3/Packages"),
                "/usr/local/www/dubalu/python-packages",
                "/usr/local/www/dubalu/django-packages"
            ]
        }
    },
    env={},
)


class LspPythonPlugin(LanguageHandler):
    def __init__(self):
        self._name = default_name
        self._config = default_config

    @property
    def name(self) -> str:
        return self._name

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
