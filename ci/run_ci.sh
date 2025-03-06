#!/bin/bash

path=${1:-.}

source ci/ci_venv.sh

black $path --exclude "ci_venv/"

echo ===== BLACK AUTOFORMATER COMPLETE =====

find $path -name "*.py" -print0 | xargs -0 pylint --rcfile=ci/.pylintrc --disable=

echo ===== PYLINT COMPLETE =====

find $path  \( -name '*.ino' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp'  \) -exec clang-format -i --style=file:ci/.clang-format {} \;

echo ===== CLANG-FORMAT COMPLETE =====
