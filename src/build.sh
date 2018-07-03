#!/bin/sh

########################################################################
# JavaScript/TypeScript/CSS/YAML/PHP/etc LS

cd tslint
npm install
tsc -p src
rm -rf node_modules
cd ..

cd javascript-typescript-langserver
npm install
tsc
rm -rf node_modules
cd ..

cd tslint-language-service
npm install
tsc
rm -rf node_modules
cd ..

cd vscode-css-languageserver
npm install
tsc
rm -rf node_modules
cd ..

cd vscode-html-languageserver
npm install
tsc
rm -rf node_modules
cd ..

npm install
npm run build

cp node_modules/typescript/lib/lib.*.ts dist/LSP-TypeScript/server

mkdir -p dist/LSP-Vue/server/rules
cp node_modules/eslint/lib/rules/*.js dist/LSP-Vue/server/rules

########################################################################
# Python LS

# download dependencies:
for platform in manylinux1_i686 manylinux1_x86_64 win32 win_amd64 macosx_10_11_x86_64; do
	for version in 33 34 35 36 37; do
		pip3 download --only-binary=:all: --implementation cp --python-version $version --platform $platform --abi cp${version}m typed-ast
	done
done

pip3 install python-language-server -t dist/LSP-Python/server
pip3 install pyflakes -t dist/LSP-Python/server
pip3 install rope -t dist/LSP-Python/server
pip3 install autopep8 -t dist/LSP-Python/server

pip3 install pyls-mypy -t dist/LSP-Python/server/py3
pip3 install typeshed -t dist/LSP-Python/server/py3
for f in dist/LSP-Python/server/*; do rm -rf dist/LSP-Python/server/py3/$(basename $f); done
for wheel in *.whl; do
	unzip -n $wheel -d dist/LSP-Python/server/py3
done

pip install future -t dist/LSP-Python/server/py2
pip install configparser -t dist/LSP-Python/server/py2
for f in dist/LSP-Python/server/*; do rm -rf dist/LSP-Python/server/py2/$(basename $f); done

rm -rf dist/LSP-Python/server/py3/mypy
ln -fs ../../../../mypy/mypy dist/LSP-Python/server/py3

rm -rf dist/LSP-Python/server/py3/pyls_mypy
ln -fs ../../../../pyls-mypy/pyls_mypy dist/LSP-Python/server/py3

rm -rf dist/LSP-Python/server/pyls
ln -fs ../../../python-language-server/pyls dist/LSP-Python/server

ln -fs ../../../pyls.py dist/LSP-Python/server

########################################################################
# Java LS
# Download milestone from http://download.eclipse.org/jdtls/milestones/

# download dependencies:
curl -LO http://ftp.jaist.ac.jp/pub/eclipse/jdtls/milestones/0.21.0/jdt-language-server-0.21.0-201806152234.tar.gz

mkdir -p dist/LSP-Java/server
cd dist/LSP-Java/server
tar xzf ../../../jdt-language-server-*.tar.gz
mv -f config_mac config_osx
mv -f config_win config_windows
cd plugins
ln -fs org.eclipse.equinox.launcher_*.jar org.eclipse.equinox.launcher.jar
cd ../../../..

# Or build from sources:

# cd eclipse.jdt.ls
# ./mvnw clean verify
# cd ..
# mkdir -p dist/LSP-Java/server
# cd dist/LSP-Java/server
# ln -fs ../../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/config_mac config_OSX
# ln -fs ../../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/config_linux config_Linux
# ln -fs ../../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/config_win config_Windows
# ln -fs ../../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/plugins
# cd plugins
# ln -fs org.eclipse.equinox.launcher_*.jar org.eclipse.equinox.launcher.jar
# cd ../../..

########################################################################
# C/C++/Objective-C LS (cquery)
mkdir -p dist/LSP-Cpp

# brew install --HEAD cquery
#   or
# git clone https://github.com/cquery-project/cquery --single-branch --depth=1
# cd cquery
# git submodule update --init && ./waf configure build --variant=debug  # --variant=debug if you want to report issues.

########################################################################
# Scala LS
./coursier fetch --cache dist/LSP-Scala/server -p ch.epfl.lamp:dotty-language-server_0.8:0.8.0
ln -fs ../../../coursier dist/LSP-Scala/server/coursier

# java -jar dist/LSP-Scala/server/coursier launch --cache dist/LSP-Scala/server ch.epfl.lamp:dotty-language-server_0.8:0.8.0 -M dotty.tools.languageserver.Main -- -stdio  # <- starts server


# External Servers:

########################################################################
# Ruby LS

gem install solargraph
# solargraph socket  # <- starts server

########################################################################
# Rust LS
brew install rustup
export PATH="~/.cargo/bin:$PATH"
rustup default nightly
rustup component add rls-preview
# rustup run nightly rls  # <- starts server

########################################################################
# Go LS
brew install go
export PATH=":~/go/bin:$PATH"
go get -u github.com/sourcegraph/go-langserver
go get -u github.com/nsf/gocode
# go-langserver  # <- starts server

########################################################################
# R LS
brew install r
# R --quiet --slave -e languageserver::run()  # <- starts server

########################################################################
# Add plugins and rsync
for plugin in dist/*; do
	plugin=$(basename $plugin)
	if [ -d plugins/$plugin ]; then
		cd dist/$plugin
		ln -fs ../../plugins/$plugin/* .
		ln -fs ../../plugins/$plugin/.* .
		cd ../..
	fi
done

noglob rsync --exclude .git --exclude '*.tar.gz' --exclude '*.pyc' --exclude '__pycache__' --exclude 'bin' -av --delete --copy-links dist/ ../servers
