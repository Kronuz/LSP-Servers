import sublime

import os
import re
import shutil
import subprocess

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.spinner import spinner

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def rustup_command():
    return "rustup"


def rustup_is_installed():
    return shutil.which(rustup_command()) is not None


def exec_child_process(cmd, cwd=None, env=None):
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore
    full_env = os.environ.copy()
    full_env.update(env)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=full_env,
        startupinfo=startupinfo)
    stdoutdata, stderrdata = map(lambda s: s.decode('utf-8') if isinstance(s, bytes) else s, proc.communicate())
    # print("% " + " ".join(cmd))
    # print(stdoutdata)
    # print(stderrdata)
    if proc.returncode:
        raise RuntimeError("{}: {}".format(proc.returncode, stderrdata))
    return stdoutdata, stderrdata


def find_file(folder, filename):
    if os.path.exists(os.path.join(folder, filename)):
        return True
    parent_folder = os.path.dirname(folder)
    if not parent_folder or folder != parent_folder:
        return False
    return find_file(parent_folder, filename)


class LspRustClientConfig(ClientConfig):
    def __init__(self):
        self.channel = "nightly"
        self.component_name = "rls-preview"

        self.name = "rust"
        self.binary_args = [
            rustup_command(),
            "run",
            self.channel,
            "rls",
        ]
        self.tcp_port = None
        self.languages = {
            "rust": {
                "scopes": ["source.rust"],
                "syntaxes": ["rust"],
            },
        }
        self.enabled = True
        self.init_options = {}
        self.settings = {}
        self.env = {}


class LspRustPlugin(LanguageHandler):
    dialogs = True

    def __init__(self):
        self._server_name = "Rust Language Server"
        self._config = LspRustClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        env = self.make_rls_env()
        if not env:
            window.status_message(
                "{} must be installed to run {}".format(rustup_command(), self._server_name))
            return False
        self._config.env.update(env)

        self.warn_on_missing_cargo_toml(window)
        self.warn_on_rls_toml(window)

        if not self.setup_rls_via_rustup(update_rustup=True):
            return False

        return True

    def on_initialized(self, client) -> None:
        client.on_notification("textDocument/publishDiagnostics", self.on_diagnostics)
        client.on_notification("window/progress", self.on_progress)

        # FIXME these are legacy notifications used by RLS ca jan 2018.
        # remove once we're certain we've progress on:
        client.on_notification("rustDocument/beginBuild", self.on_progress)
        client.on_notification("rustDocument/diagnosticsEnd", self.on_progress)

    def on_diagnostics(self, params):
        spinner.start(spinner='monkey')

    def on_progress(self, params):
        spinner.start(spinner='fire')

    def warn_on_missing_cargo_toml(self, window):
        for folder in window.folders():
            if find_file(folder, "Cargo.toml"):
                break
        else:
            sublime.status_message("'A Cargo.toml file must be at the root of the workspace in order to support all features")

    def warn_on_rls_toml(self, window):
        for folder in window.folders():
            if find_file(folder, "rls.toml"):
                sublime.status_message("Found deprecated rls.toml. Use user settings instead (Preferences: LSP Settings)")
                break

    def make_rls_env(self, set_lib_path=False):
        """
        Make an evironment to run the RLS.
        Tries to synthesise RUST_SRC_PATH for Racer, if one is not already set.
        """
        env = {}
        env['PATH'] = os.pathsep.join(os.environ.get('PATH', "").split(os.pathsep) + [os.path.expanduser("~/.cargo/bin")])
        try:
            stdoutdata, stderrdata = exec_child_process([
                rustup_command(),
                "run",
                self._config.channel,
                "rustc",
                "--print",
                "sysroot",
            ], env=env)
        except RuntimeError:
            print("RLS could not set RUST_SRC_PATH for Racer because it could not read the Rust sysroot.")
            return None
        except IOError:
            print("Rustup not available. Install from https://www.rustup.rs/")
            return None

        sysroot = stdoutdata.strip()
        print("Setting sysroot to '{}'".format(sysroot))
        RUST_SRC_PATH = os.environ.get('RUST_SRC_PATH')
        if RUST_SRC_PATH:
            env['RUST_SRC_PATH'] = RUST_SRC_PATH
        else:
            env['RUST_SRC_PATH'] = os.path.join(sysroot, "lib", "rustlib", "src", "rust", "src")

        if set_lib_path:
            env['DYLD_LIBRARY_PATH'] = os.pathsep.join(os.environ.get('DYLD_LIBRARY_PATH', "").split(os.pathsep) + [os.path.join(sysroot, "lib")])
            env['LD_LIBRARY_PATH'] = os.pathsep.join(os.environ.get('LD_LIBRARY_PATH', "").split(os.pathsep) + [os.path.join(sysroot, "lib")])
        return env

    def ensure_toolchain(self):
        if self.has_toolchain():
            return True
        if LspRustPlugin.dialogs and sublime.ok_cancel_dialog(
            "{} toolchain not installed.\n"
            "Install now?".format(self._config.channel)
        ):
            return self.try_to_install_toolchain()
        LspRustPlugin.dialogs = False
        return False

    def has_toolchain(self):
        try:
            stdoutdata, stderrdata = exec_child_process([
                rustup_command(),
                "toolchain",
                "list",
            ], env=self._config.env)
        except RuntimeError:
            print("Unexpected error initialising RLS - error running rustup")
            return False

        return self._config.channel in stdoutdata

    def try_to_install_toolchain(self):
        spinner.start("LSP-Rust", "Installing toolchain…", timeout=-1)
        try:
            stdoutdata, stderrdata = exec_child_process([
                rustup_command(),
                "toolchain",
                "install",
                self._config.channel,
            ], env=self._config.env)
        except RuntimeError:
            spinner.stop("Could not install {} toolchain".format(self._config.channel))
            return False

        spinner.stop("{} toolchain installed successfully".format(self._config.channel))
        return True

    def check_for_rls(self):
        if self.has_rls_components():
            return True
        if LspRustPlugin.dialogs and sublime.ok_cancel_dialog(
            "RLS not installed\n"
            "Install now?"
        ):
            return self.install_rls()
        LspRustPlugin.dialogs = False
        return False

    def has_rls_components(self):
        try:
            stdoutdata, stderrdata = exec_child_process([
                rustup_command(),
                "component",
                "list",
                "--toolchain",
                self._config.channel,
            ], env=self._config.env)
        except RuntimeError:
            print("Unexpected error initialising RLS - error running rustup")
            return False

        return (
            re.search(r'^rust-analysis.* \((default|installed)\)$', stdoutdata, re.MULTILINE) and
            re.search(r'^rust-src.* \((default|installed)\)$', stdoutdata, re.MULTILINE) and
            re.search(r'^' + self._config.component_name + r'.* \((default|installed)\)$', stdoutdata, re.MULTILINE)
        )

    def install_component(self, component):
        try:
            stdoutdata, stderrdata = exec_child_process([
                rustup_command(),
                "component",
                "add",
                component,
                "--toolchain",
                self._config.channel,
            ], env=self._config.env)
        except RuntimeError:
            return False
        return True

    def install_rls(self):
        spinner.start("LSP-Rust", "Installing components…", timeout=-1)
        if not self.install_component('rust-analysis'):
            spinner.stop("Could not install RLS: rust-analysis")
            return False
        if not self.install_component('rust-src'):
            spinner.stop("Could not install RLS: rust-src")
            return False
        if not self.install_component(self._config.component_name):
            spinner.stop("Could not install RLS: {}".format(self._config.component_name))
            return False
        spinner.stop("RLS components installed successfully")
        return True

    def rustup_update(self):
        spinner.start("LSP-Rust", "Updating…", timeout=-1)
        try:
            stdoutdata, stderrdata = exec_child_process([
                rustup_command(),
                "update",
            ], env=self._config.env)
        except RuntimeError:
            spinner.stop("An error occurred whilst trying to update.")
            return False

        # This test is imperfect because if the user has multiple toolchains installed, they
        # might have one updated and one unchanged. But I don't want to go too far down the
        # rabbit hole of parsing rustup's output.
        if "unchanged" in stdoutdata:
            spinner.stop("Up to date.")
        else:
            spinner.stop("Up to date. Restart Sublime Text for changes to take effect.")
        return True

    def setup_rls_via_rustup(self, update_rustup=False):
        try:
            if update_rustup:
                if not self.rustup_update():
                    print("Could not update Rustup")
            if not self.ensure_toolchain():
                print("Could not start RLS: toolchain")
                return False
            if not self.check_for_rls():
                print("Could not start RLS: rls")
                return False
            return True
        except IOError:
            print("Rustup not available. Install from https://www.rustup.rs/")
        except Exception as err:
            print("Failed to run command:", err)


def plugin_loaded():
    if not rustup_is_installed():
        sublime.message_dialog(
            "Rustup not available. Install from https://www.rustup.rs/")
