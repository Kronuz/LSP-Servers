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


def configure(name, scopes, syntaxes, languageId):
    return ClientConfig(
        name=name,
        binary_args=[
            node_command(),
            os.path.join(server_path, "css-languageserver.js"),
            "--stdio"
        ],
        tcp_port=None,
        scopes=scopes,
        syntaxes=syntaxes,
        languageId=languageId,
        enabled=True,
        init_options={},
        settings={},
        env={},
    )


class LspCssPlugin(LanguageHandler):
    def __init__(self):
        self._name = "css"
        self._server_name = "CSS Language Server"
        self._config = configure(
            self._name,
            ["source.css"],
            ["css"],
            "css",
        )

    @property
    def name(self) -> str:
        return self._name

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
        pass  # extra initialization here.


class LspScssPlugin(LanguageHandler):
    def __init__(self):
        self._name = "scss"
        self._server_name = "SCSS Language Server"
        self._config = configure(
            self._name,
            ["source.scss"],
            ["scss"],
            "scss",
        )

    @property
    def name(self) -> str:
        return self._name

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
        pass  # extra initialization here.


class LspSassPlugin(LanguageHandler):
    def __init__(self):
        self._name = "sass"
        self._server_name = "Sass Language Server"
        self._config = configure(
            self._name,
            ["source.sass"],
            ["sass"],
            "sass",
        )

    @property
    def name(self) -> str:
        return self._name

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
        pass  # extra initialization here.


class LspLessPlugin(LanguageHandler):
    def __init__(self):
        self._name = "less"
        self._server_name = "LESS Language Server"
        self._config = configure(
            self._name,
            ["source.less"],
            ["less"],
            "less",
        )

    @property
    def name(self) -> str:
        return self._name

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
        pass  # extra initialization here.


def plugin_loaded():
    if not node_is_installed():
        sublime.message_dialog(
            "Please install Node.js")
