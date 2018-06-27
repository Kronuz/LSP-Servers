import sublime

import os
import shutil

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def java_command():
    return "java"


def java_is_installed():
    return shutil.which(java_command()) is not None


class LspScalaClientConfig(ClientConfig):
    def __init__(self):
        self.name = "scala"
        self.binary_args = [
            java_command(),
            "-jar",
            os.path.join(server_path, "coursier"),
            "launch",
            "--cache",
            server_path,
            "ch.epfl.lamp:dotty-language-server_0.8:0.8.0",
            "-M",
            "dotty.tools.languageserver.Main",
            "--",
            "-stdio"
        ]
        self.tcp_port = None
        self.languages = {
            "scala": {
                "scopes": ["source.scala"],
                "syntaxes": ["scala"],
            },
        }
        self.enabled = True
        self.init_options = {}
        self.settings = {}
        self.env = {}


class LspScalaPlugin(LanguageHandler):
    def __init__(self):
        self._server_name = "Scala Language Server"
        self._config = LspScalaClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not java_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(node_command()), self._server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        pass  # extra initialization here.


def plugin_loaded():
    if not java_is_installed():
        sublime.message_dialog(
            "Please install Java")
