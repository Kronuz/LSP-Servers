#!/bin/sh

########################################################################
# JavaScript/TypeScript/CSS/YAML/PHP/etc LS

cd tslint
npm install
tsc -p src
mv node_modules \~node_modules
cd ..

cd javascript-typescript-langserver
npm install
tsc
mv node_modules \~node_modules
cd ..

cd vscode-css-languageserver
npm install
tsc
mv node_modules \~node_modules
cd ..

npm install
npm run build

cp node_modules/typescript/lib/lib.*.ts dist/typescript

########################################################################
# Python LS

pip3 install python-language-server -t dist/python
pip3 install pyflakes -t dist/python
pip3 install rope -t dist/python
pip3 install autopep8 -t dist/python

pip3 install pyls-mypy -t dist/python/py3
pip3 install typeshed -t dist/python/py3
for f in dist/python/*; do rm -rf dist/python/py3/$(basename $f); done
for platform in manylinux1_i686 manylinux1_x86_64 win32 win_amd64 macosx_10_11_x86_64; do
	for version in 33 34 35 36; do
		pip3 download --only-binary=:all: --implementation cp --python-version $version --platform $platform --abi cp${version}m typed-ast
	done
done
for wheel in *.whl; do
	unzip -n $wheel -d dist/python/py3
done

pip install future -t dist/python/py2
pip install configparser -t dist/python/py2
for f in dist/python/*; do rm -rf dist/python/py2/$(basename $f); done

rm -rf dist/python/py3/mypy
ln -fs ../../../mypy/mypy dist/python/py3

rm -rf dist/python/py3/pyls_mypy
ln -fs ../../../pyls-mypy/pyls_mypy dist/python/py3

rm -rf dist/python/pyls
ln -fs ../../python-language-server/pyls dist/python

ln -fs ../../pyls.py dist/python

########################################################################
# Java LS
# Download milestone from http://download.eclipse.org/jdtls/milestones/

mkdir -p dist/java
cd dist/java
curl -LO http://ftp.jaist.ac.jp/pub/eclipse/jdtls/milestones/0.21.0/jdt-language-server-0.21.0-201806152234.tar.gz
tar xzf jdt-language-server-*.tar.gz
mv -f config_mac config_OSX
mv -f config_linux config_Linux
mv -f config_win config_Windows
cd plugins
ln -fs org.eclipse.equinox.launcher_*.jar org.eclipse.equinox.launcher.jar
cd ../../..

# Or build from sources:

# cd eclipse.jdt.ls
# ./mvnw clean verify
# cd ..
# mkdir -p dist/java
# cd dist/java
# ln -fs ../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/config_mac config_OSX
# ln -fs ../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/config_linux config_Linux
# ln -fs ../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/config_win config_Windows
# ln -fs ../../eclipse.jdt.ls/org.eclipse.jdt.ls.product/target/repository/plugins
# cd plugins
# ln -fs org.eclipse.equinox.launcher_*.jar org.eclipse.equinox.launcher.jar
# cd ../../..

########################################################################
# Scala LS
./coursier fetch --cache dist/scala -p ch.epfl.lamp:dotty-language-server_0.8:0.8.0
ln -fs ../../coursier dist/scala/coursier
# java -jar dist/scala/coursier launch --cache dist/scala ch.epfl.lamp:dotty-language-server_0.8:0.8.0 -M dotty.tools.languageserver.Main -- -stdio  # <- starts server


# External Servers:

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
noglob rsync --exclude .git --exclude '*.tar.gz' --exclude '*.pyc' --exclude '__pycache__' --exclude 'bin' -av --delete --copy-links dist/ ../servers
