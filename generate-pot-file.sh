#!/bin/sh
# This script generates the po/collision.pot file
FILEPATH="$(readlink -f "$0")"
DIR="$(dirname "$FILEPATH")"
cd "$DIR"
xgettext --package-name=collision \
         --package-version=0.0.1 \
         --copyright-holder='Bruno Nova <brunomb.nova@gmail.com>' \
         -cTRANSLATORS \
         -L Python \
         -s -o "po/collision.pot" \
         *.py

# To create a .po:
# $ msginit -i collision.pot -l LANG
#
# To update a .po:
# $ msgmerge -U LANG.po collision.pot
#
# To compile a .po into an .mo:
# $ msgfmt LANG.po
