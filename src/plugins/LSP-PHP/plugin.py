import sublime

import os
import shutil

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def node_command():
    return "node"


def node_is_installed():
    return shutil.which(node_command()) is not None


server_name = "PHP Language Server"
default_name = "php"
default_config = ClientConfig(
    name=default_name,
    binary_args=[
        node_command(),
        os.path.join(server_path, "intelephense-server.js"),
        "--stdio"
    ],
    tcp_port=None,
    scopes=["source.php", "embedding.php text.html.basic"],
    syntaxes=["php"],
    languageId="php",
    enabled=True,
    init_options={
        "storagePath": "/tmp/.lsp/intelephense"
    },
    settings={},
    env={},
)


class LspPhpPlugin(LanguageHandler):
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
        if not node_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(node_command()), server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        pass  # extra initialization here.


def plugin_loaded():
    if not node_is_installed():
        sublime.message_dialog(
            "Please install Node.js")
