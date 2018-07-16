import sublime

import os
import shutil

from SublimeCodeIntel.plugin.core.settings import ClientConfig
from SublimeCodeIntel.plugin.core.handlers import LanguageHandler
from SublimeCodeIntel.plugin.core.spinner import spinner

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def node_command():
    return "node"


def node_is_installed():
    return shutil.which(node_command()) is not None


class CodeIntelMarkdownClientConfig(ClientConfig):
    def __init__(self):
        self.name = "markdown"
        self.binary_args = [
            node_command(),
            os.path.join(server_path, "markdown-language-server.js"),
            "--stdio"
        ]
        self.tcp_port = None
        self.languages = {
            "markdown": {
                "scopes": ["text.html.markdown"],
                "syntaxes": ["markdown"],
            },
        }
        self.enabled = True
        self.init_options = {}
        self.settings = {}
        self.env = {}


class CodeIntelMarkdownPlugin(LanguageHandler):
    def __init__(self):
        self._server_name = "Markdown Language Server"
        self._config = CodeIntelMarkdownClientConfig()

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
        spinner.start("Markdown-CodeIntel", spinner='monkey')


def plugin_loaded():
    if not node_is_installed():
        sublime.message_dialog(
            "Please install Node.js")
