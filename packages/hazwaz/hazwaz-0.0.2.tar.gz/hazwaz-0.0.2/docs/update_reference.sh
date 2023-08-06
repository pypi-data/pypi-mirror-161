#!/bin/sh

# This script generates new autodoc files for the hazwaz reference, overwriting
# all existing files.

cd $(dirname "$0")/..

echo "This will overwrite all existing files in the docs/source/reference/"
echo "continue? (press enter to continue, or ctrl-C to abort)"

read continue

sphinx-apidoc -f -e -M -o docs/source/reference/ hazwaz $*
