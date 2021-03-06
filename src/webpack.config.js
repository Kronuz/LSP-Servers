const path = require('path');
const webpack = require('webpack');
const Template = require("webpack/lib/Template");
const intersect = require("webpack/lib/util/SetHelpers").intersect;
const ContextModule = require("webpack/lib/ContextModule");
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')


// Monkey-patch getSourceForEmptyContext so it does do a require()
function getSourceForEmptyContext(id) {
    return `function webpackEmptyContext(req) {
  return require(req);
}
webpackEmptyContext.keys = function() { return []; };
webpackEmptyContext.resolve = require.resolve;
module.exports = webpackEmptyContext;
webpackEmptyContext.id = ${JSON.stringify(id)};`;
}
ContextModule.prototype.getSourceForEmptyContext = getSourceForEmptyContext;


function getAllAsyncChunks() {
  const queue = new Set();
  const chunks = new Set();

  const initialChunks = intersect(
    Array.from(this.groupsIterable, g => new Set(g.chunks))
  );

  for (const chunkGroup of this.groupsIterable) {
    for (const child of chunkGroup.childrenIterable) {
      queue.add(child);
    }
  }

  for (const chunkGroup of queue) {
    for (const chunk of chunkGroup.chunks) {
      if (!initialChunks.has(chunk)) {
        chunks.add(chunk);
      }
    }
    for (const child of chunkGroup.childrenIterable) {
      queue.add(child);
    }
  }

  for (const chunk of Array.from(this.groupsIterable)[0].chunks) {
    chunks.add(chunk);
  }

  return chunks;
}


function getChunkMaps(realHash) {
  const chunkHashMap = Object.create(null);
  const chunkContentHashMap = Object.create(null);
  const chunkNameMap = Object.create(null);

  for (const chunk of getAllAsyncChunks.call(this)) {
    chunkHashMap[chunk.id] = realHash ? chunk.hash : chunk.renderedHash;
    for (const key of Object.keys(chunk.contentHash)) {
      if (!chunkContentHashMap[key]) {
        chunkContentHashMap[key] = Object.create(null);
      }
      chunkContentHashMap[key][chunk.id] = chunk.contentHash[key];
    }
    if (chunk.name) {
      chunkNameMap[chunk.id] = chunk.name;
    }
  }

  return {
    hash: chunkHashMap,
    contentHash: chunkContentHashMap,
    name: chunkNameMap
  };
}


function getAssetPathSrc(path, hash, chunk, chunkIdExpression, contentHashType) {
  // from JsonpMainTemplatePluggin.getScriptSrcPath()
  const chunkMaps = getChunkMaps.call(chunk);
  return this.getAssetPath(path, {
    hash: `" + ${this.renderCurrentHashCode(hash)} + "`,
    hashWithLength: length =>
      `" + ${this.renderCurrentHashCode(hash, length)} + "`,
    chunk: {
      id: `" + ${chunkIdExpression} + "`,
      hash: `" + ${JSON.stringify(chunkMaps.hash)}[${chunkIdExpression}] + "`,
      hashWithLength(length) {
        const shortChunkHashMap = Object.create(null);
        for (const chunkId of Object.keys(chunkMaps.hash)) {
          if (typeof chunkMaps.hash[chunkId] === "string") {
            shortChunkHashMap[chunkId] = chunkMaps.hash[chunkId].substr(
              0,
              length
            );
          }
        }
        return `" + ${JSON.stringify(
          shortChunkHashMap
        )}[${chunkIdExpression}] + "`;
      },
      name: `" + (${JSON.stringify(
        chunkMaps.name
      )}[${chunkIdExpression}]||${chunkIdExpression}) + "`,
      contentHash: {
        [contentHashType]: `" + ${JSON.stringify(
          chunkMaps.contentHash[contentHashType]
        )}[${chunkIdExpression}] + "`
      },
      contentHashWithLength: {
        [contentHashType]: length => {
          const shortContentHashMap = {};
          const contentHash = chunkMaps.contentHash[contentHashType];
          for (const chunkId of Object.keys(contentHash)) {
            if (typeof contentHash[chunkId] === "string") {
              shortContentHashMap[chunkId] = contentHash[chunkId].substr(
                0,
                length
              );
            }
          }
          return `" + ${JSON.stringify(
            shortContentHashMap
          )}[${chunkIdExpression}] + "`;
        }
      }
    },
    contentHashType
  });
}


class DependenciesLoaderPlugin {

  apply(compiler) {
    compiler.hooks.thisCompilation.tap(
      "DependenciesLoaderPlugin",
      compilation => {
        compilation.mainTemplate.hooks.localVars.tap(
          "DependenciesLoaderPlugin",
          (source, chunk, hash) => {
            const entries = [chunk.entryModule].filter(Boolean).map(m =>
              [m.id].concat(
                Array.from(chunk.groupsIterable)[0]
                  .chunks.filter(c => c !== chunk)
                  .map(c => c.id)
              )
            );

            return Template.asString([
              source,
              "",
              "// Load deferred chunks",
              "function scriptSrc(chunkId) {",
              Template.indent([
                `return ${getAssetPathSrc.call(
                  compilation.mainTemplate,
                  JSON.stringify(compilation.mainTemplate.outputOptions.chunkFilename),
                  hash,
                  chunk,
                  "chunkId",
                  "javascript"
                )}`
              ]),
              "}",
              "function loadDeferred(chunkId) {",
              Template.indent([
                "var src = scriptSrc(chunkId);",
                "var chunk = require(__dirname + '/' + src);",
                "var moreModules = chunk.modules, chunkIds = chunk.ids;",
                "for(var moduleId in moreModules) {",
                Template.indent([
                  "modules[moduleId] = moreModules[moduleId];",
                ]),
                "}",
              ]),
              "}",
              "var deferredModules = [",
              Template.indent([entries.map(e => JSON.stringify(e)).join(", ")]),
              "];",
              "for (var i = 0; i < deferredModules.length; ++i) {",
              Template.indent([
                "var deferredModule = deferredModules[i];",
                "for (var j = 1; j < deferredModule.length; ++j) {",
                Template.indent([
                  "var chunkId = deferredModule[j];",
                  "loadDeferred(chunkId);"
                ]),
                "}",
              ]),
              "}",
            ]);
          }
        );
      }
    );
  }
}

function language(name, entry, externals) {
  return {
    mode: "production",
    target: "node",
    node: {
      __dirname: false,
      __filename: false,
    },
    output: {
      path: path.join(__dirname, 'dist', name, 'server'),
      libraryTarget: "commonjs2",
    },
    entry: entry,
    module: {
      rules: [
        {
          test: /\.js$/,
          use: 'shebang-loader',
        }
      ],
    },
    plugins: [
      new webpack.HashedModuleIdsPlugin(),  // or webpack.NamedModulesPlugin()
      new DependenciesLoaderPlugin(),
    ],
    optimization: {
      // minimize: false,
      minimizer: [
        new UglifyJsPlugin({
            cache: true,
            parallel: true,
            uglifyOptions: {
                compress: false,  // slower without this
                sourceMap: false,
                output: {
                  beautify: true,
                  semicolons: false,
                  indent_level: 1
                }
            }
        }),
      ],
      // splitChunks: {
      //   chunks: 'all',
      // },
    },
    externals,
  };
}

module.exports = [
  language('JavaScript-CodeIntel', {"lsp-tsserver/dist/server": "lsp-tsserver/dist/server", "node_modules/tslint-language-service": "tslint-language-service", "node_modules/eslint-language-service": "eslint-language-service"}, ['eslint', 'tslint']),
  language('JavaScript-CodeIntel', {"node_modules/eslint": "eslint", "node_modules/tslint": "tslint"}),
  language('PHP-CodeIntel', {"intelephense-server": "intelephense-server"}),
  language('Markdown-CodeIntel', {"markdown-language-server": "markdown-language-server/dist/src/main"}),
  language('CSS-CodeIntel', {"css-languageserver": "vscode-css-languageserver/out/cssServerMain"}),
  language('HTML-CodeIntel', {"html-languageserver": "vscode-html-languageserver/out/htmlServerMain"}),
  language('JSON-CodeIntel', {"vscode-json-languageserver": "vscode-json-languageserver/out/jsonServerMain"}),
  language('YAML-CodeIntel', {"yaml-language-server": "yaml-language-server/out/server/src/server"}),
  language('OCaml-CodeIntel', {"ocaml-language-server": "ocaml-language-server/bin/server/index"}),
  language('Vue-CodeIntel', {"vue-language-server": "vue-language-server/dist/vueServerMain"}, './lib-cov/stylus'),
  // language('Flow-CodeIntel', {"flow-language-server": "flow-language-server/lib/bin/cli"}, ['axios', 'hipchat-notifier', 'loggly', 'mailgun-js', 'nodemailer', 'slack-node', 'encoding', 'original-fs', 'spawn-sync']),
];
