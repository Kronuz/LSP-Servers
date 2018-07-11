import sublime

import os
import shutil

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.spinner import spinner

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def java_command():
    return "java"


def java_is_installed():
    return shutil.which(java_command()) is not None


class LspJavaClientConfig(ClientConfig):
    def __init__(self):
        self.name = "java"
        self.binary_args = [
            java_command(),
            "-jar",
            os.path.join(server_path, "plugins", "org.eclipse.equinox.launcher.jar"),
            "-configuration",
            os.path.join(server_path, "config_%s" % sublime.platform()),
        ]
        self.tcp_port = None
        self.languages = {
            "java": {
                "scopes": ["source.java"],
                "syntaxes": ["java"],
            },
        }
        self.enabled = True
        self.init_options = {}
        self.settings = {}
        self.env = {}


class LspJavaPlugin(LanguageHandler):
    def __init__(self):
        self._server_name = "Java Language Server"
        self._config = LspJavaClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not java_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(java_command()), self._server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        client.on_notification("textDocument/publishDiagnostics", self.on_diagnostics)

    def on_diagnostics(self, params):
        spinner.start("LSP-Java", spinner='monkey')


def plugin_loaded():
    if not java_is_installed():
        sublime.message_dialog(
            "Please install Java")
