#!/bin/sh

set -x

find $DLREPO_ROOT_DIR

if [ -f file.txt ]; then
	echo finalized >> file.txt
	touch finalized
elif [ -f file3.txt ]; then
	echo fail
	exit 1
fi
