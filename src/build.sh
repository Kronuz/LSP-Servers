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

pip install future -t dist/python/compat
pip install configparser -t dist/python/compat
rm -rf dist/python/compat/future
rm -rf dist/python/compat/future-*
rm -rf dist/python/compat/libfuturize
rm -rf dist/python/compat/libpasteurize
rm -rf dist/python/compat/past

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
noglob rsync --exclude .git --exclude '*.tar.gz' --exclude '*.pyc' --exclude '__pycache__' --exclude 'bin' -av --delete --copy-links dist/ ../servers
