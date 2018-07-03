import sublime

import os
import shutil

from LSP.plugin.core.settings import ClientConfig
from LSP.plugin.core.handlers import LanguageHandler

package_path = os.path.dirname(__file__)
server_path = os.path.join(package_path, 'server')


def cquery_command():
    # brew install --HEAD cquery
    return "cquery"


def cquery_is_installed():
    return shutil.which(cquery_command()) is not None


class LspCppClientConfig(ClientConfig):
    def __init__(self):
        self.name = "cpp"
        self.binary_args = [
            cquery_command(),
            "--log-file",
            "~/.lsp/cquery.log"
        ]
        self.tcp_port = None
        self.languages = {
            "c": {
                "scopes": ["source.c"],
                "syntaxes": ["c"],
            },
            "c++": {
                "scopes": ["source.c++"],
                "syntaxes": ["c++"],
            },
            "objc": {
                "scopes": ["source.objc"],
                "syntaxes": ["Objective-C"],
            },
            "objc++": {
                "scopes": ["source.objc++"],
                "syntaxes": ["Objective-C++"],
            },
        }
        self.enabled = True
        self.init_options = {
            # Allow indexing on textDocument/didChange.
            # May be too slow for big projects, so it is off by default.
            # "enableIndexOnDidChange": False,

            # Root directory of the project. **Not available for configuration**
            # "projectRoot": "",

            # If specified, this option overrides compile_commands.json and this
            # external command will be executed with an option |projectRoot|.
            # The initialization options will be provided as stdin.
            # The stdout of the command should be the JSON compilation database.
            # "compilationDatabaseCommand: "",

            # Directory containing compile_commands.json.
            # "compilationDatabaseDirectory": "",

            # Cache directory for indexed files.
            "cacheDirectory": os.path.expanduser("~/.lsp/cquery"),

            # Cache serialization format.
            #
            # "json" generates `cacheDirectory/.../xxx.json` files which can be pretty
            # printed with jq.
            #
            # "msgpack" uses a compact binary serialization format (the underlying wire
            # format is [MessagePack](https://msgpack.org/index.html)) which typically
            # takes only 60% of the corresponding JSON size, but is difficult to inspect.
            # msgpack does not store map keys and you need to re-index whenever a struct
            # member has changed.
            # "cacheFormat": "json",

            # Value to use for clang -resource-dir if not present in
            # compile_commands.json.
            #
            # cquery includes a resource directory, this should not need to be configured
            # unless you're using an esoteric configuration. Consider reporting a bug and
            # fixing upstream instead of configuring this.
            #
            # Example value: "/path/to/lib/clang/5.0.1/"
            # "resourceDirectory": "",

            # Additional arguments to pass to clang.
            "extraClangArguments": [
                "-Wno-inconsistent-missing-override",
                "-Wno-format",
                "-Wno-extern-c-compat"
            ],

            # If True, cquery will send progress reports while indexing
            # How often should cquery send progress report messages?
            #  -1: never
            #   0: as often as possible
            #   xxx: at most every xxx milliseconds
            #
            # Empty progress reports (ie, idle) are delivered as often as they are
            # available and may exceed this value.
            #
            # This does not guarantee a progress report will be delivered every
            # interval; it could take significantly longer if cquery is completely idle.
            # "progressReportFrequencyMs": 500,

            # If True, document links are reported for #include directives.
            # "showDocumentLinksOnIncludes": True,

            # Version of the client. If undefined the version check is skipped. Used to
            # inform users their vscode client is too old and needs to be updated.
            # "clientVersion": 1,

            "client": {
                # TextDocumentClientCapabilities.completion.completionItem.snippetSupport
                # "snippetSupport": False
            },

            "codeLens": {
                # Enables code lens on parameter and function variables.
                # "localVariables": True
            },

            "completion": {
                # Some completion UI, such as Emacs' completion-at-point and company-lsp,
                # display completion item label and detail side by side.
                # This does not look right, when you see things like:
                #     "foo" "int foo()"
                #     "bar" "void bar(int i = 0)"
                # When this option is enabled, the completion item label is very detailed,
                # it shows the full signature of the candidate.
                # The detail just contains the completion item parent context.
                # Also, in this mode, functions with default arguments,
                # generates one more item per default argument
                # so that the right function call can be selected.
                # That is, you get something like:
                #     "int foo()" "Foo"
                #     "void bar()" "Foo"
                #     "void bar(int i = 0)" "Foo"
                # Be wary, this is quickly quite verbose,
                # items can end up truncated by the UIs.
                "detailedLabel": True,

                # On large projects, completion can take a long time. By default if cquery
                # receives multiple completion requests while completion is still running
                # it will only service the newest request. If this is set to False then all
                # completion requests will be serviced.
                # "dropOldRequests": True,

                # If True, filter and sort completion response. cquery filters and sorts
                # completions to try to be nicer to clients that can't handle big numbers
                # of completion candidates. This behaviour can be disabled by specifying
                # False for the option. This option is the most useful for LSP clients
                # that implement their own filtering and sorting logic.
                "filterAndSort": False,

                # Regex patterns to match include completion candidates against. They
                # receive the absolute file path.
                #
                # For example, to hide all files in a /CACHE/ folder, use ".*/CACHE/.*"
                "includeBlacklist": [
                    ".*/deprecated/.*"
                ],

                # Maximum path length to show in completion results. Paths longer than this
                # will be elided with ".." put at the front. Set to 0 or a negative number
                # to disable eliding.
                # "includeMaxPathSize": 30,

                # Whitelist that file paths will be tested against. If a file path does not
                # end in one of these values, it will not be considered for
                # auto-completion. An example value is { ".h", ".hpp" }
                # default are .h, .hh, .hpp.
                # values given here will be appended to the defaults.
                # This is significantly faster than using a regex.
                "includeSuffixWhitelist": [
                    ".hxx"
                ]
            },

            "diagnostics": {
                # Like index.{whitelist,blacklist}, don't publish diagnostics to
                # blacklisted files.
                "blacklist": [
                    ".*/deprecated/.*"
                ],

                # How often should cquery publish diagnostics in completion?
                #  -1: never
                #   0: as often as possible
                #   xxx: at most every xxx milliseconds
                # "frequencyMs": 0,

                # If True, diagnostics from a full document parse will be reported.
                # "onParse": True,

                # "whitelist": []
            },

            "highlight": {
                # Like index.{whitelist,blacklist}, don't publish semantic highlighting to
                # blacklisted files.
                # "blacklist": [],

                # "whitelist": [],
            },

            "index": {
                # Attempt to convert calls of make* functions to constructors based on
                # hueristics.
                #
                # For example, this will show constructor calls for std::make_unique
                # invocations. Specifically, cquery will try to attribute a ctor call
                # whenever the function name starts with make (ignoring case).
                # "attributeMakeCallsToCtor": True,

                # If a translation unit's absolute path matches any EMCAScript regex in the
                # whitelist, or does not match any regex in the blacklist, it will be
                # indexed. To only index files in the whitelist, add ".*" to the blacklist.
                # `std::regex_search(path, regex, std::regex_constants::match_any)`
                #
                # Example: `ash/.*\.cc`
                # "blacklist": [],

                # 0: none, 1: Doxygen, 2: all comments
                # Plugin support for clients:
                # - https://github.com/emacs-lsp/lsp-ui
                # - https://github.com/autozimu/LanguageClient-neovim/issues/224
                # "comments: 2,

                # If False, the indexer will be disabled.
                # "enabled": True,

                # If True, project paths that were skipped by the whitelist/blacklist will
                # be logged.
                # "logSkippedPaths": False,

                # Number of indexer threads. If 0, 80% of cores are used.
                # "threads": 0,

                # "whitelist": []
            },

            "workspaceSymbol": {
                # Maximum workspace search results.
                # "maxNum": 1000,

                # If True, workspace search results will be dynamically rescored/reordered
                # as the search progresses. Some clients do their own ordering and assume
                # that the results stay sorted in the same order as the search progresses.
                # "sort": True
            },

            "xref": {
                # If True, |Location[]| response will include lexical container.
                # "container": False,

                # Maximum number of definition/reference/... results.
                # "maxNum": 2000
            },

            # For debugging
            # Dump AST after parsing if some pattern matches the source filename.
            # "dumpAST": [],
        }
        self.settings = {}
        self.env = {}


class LspCppPlugin(LanguageHandler):
    def __init__(self):
        self._server_name = "C/C++/Objective-C Language Server"
        self._config = LspCppClientConfig()

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        if not cquery_is_installed():
            window.status_message(
                "{} must be installed to run {}".format(cquery_command()), self._server_name)
            return False
        return True

    def on_initialized(self, client) -> None:
        client.on_notification("textDocument/publishDiagnostics", self.on_diagnostics)
        client.on_notification("$cquery/progress", self.on_progress)

    def on_diagnostics(self, params):
        self.spinner.start('monkey')

    def on_progress(self, params):
        self.spinner.start('fire')


def plugin_loaded():
    if not cquery_is_installed():
        sublime.message_dialog(
            "Please install cquery")
