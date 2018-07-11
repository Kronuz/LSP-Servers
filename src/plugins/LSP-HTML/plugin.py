import sublime

import os
import shutil

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.spinner import spinner

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def node_command():
    return "node"


def node_is_installed():
    return shutil.which(node_command()) is not None


class LspHtmlClientConfig(ClientConfig):
    def __init__(self):
        self.name = "html"
        self.binary_args = [
            node_command(),
            os.path.join(server_path, "html-languageserver.js"),
            "--stdio",
        ]
        self.tcp_port = None
        self.languages = {
            "html": {
                "scopes": ["text.html.basic"],
                "syntaxes": ["html"],
            },
        }
        self.enabled = True
        self.init_options = {}
        self.settings = {}
        self.env = {}


class LspHtmlPlugin(LanguageHandler):
    def __init__(self):
        self._server_name = "HTML Language Server"
        self._config = LspHtmlClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not node_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(node_command()), self._server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        client.on_notification("textDocument/publishDiagnostics", self.on_diagnostics)

    def on_diagnostics(self, params):
        spinner.start("LSP-HTML", spinner='monkey')


def plugin_loaded():
    if not node_is_installed():
        sublime.message_dialog(
            "Please install Node.js")
