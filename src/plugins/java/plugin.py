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


server_name = "Java Language Server"
default_name = "java"
default_config = ClientConfig(
    name=default_name,
    binary_args=[
        java_command(),
        "-jar",
        os.path.join(server_path, "plugins", "org.eclipse.equinox.launcher.jar"),
        "-configuration",
        os.path.join(server_path, "config_%s" % platform),
    ],
    tcp_port=None,
    scopes=["source.java"],
    syntaxes=["java"],
    languageId="java",
    enabled=False,
    init_options={},
    settings={},
    env={},
)


class LspJavaPlugin(LanguageHandler):
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
        if not java_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(node_command()), server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        pass  # extra initialization here.


def plugin_loaded():
    if not java_is_installed():
        sublime.message_dialog(
            "Please install Java")
