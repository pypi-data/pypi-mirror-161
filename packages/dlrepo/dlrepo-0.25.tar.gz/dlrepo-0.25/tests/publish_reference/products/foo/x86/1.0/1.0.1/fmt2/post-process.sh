#!/bin/sh
# Copyright (c) 2022 Julien Floret
# Copyright (c) 2022 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

# Example script to use as DLREPO_POST_PROCESS_CMD.
#
# It checks if the format contains a deb or rpm repository and signs the
# packages with the current user's default gpg key. The key must not have any
# passphrase.
#
# The command is executed with $PWD as the format folder

# Our key has no passphrase to be asked, silence GPG_TTY warning
export GPG_TTY=

. /etc/default/dlrepo

: ${GNUPGHOME:=/etc/dlrepo/gnupg}
export GNUPGHOME

: ${GPG_KEY:=$(gpg --list-keys 2>&1 | sed -n 's/^uid.*<\(.\+@.\+\)>$/\1/p')}
: ${GPG_OPTS:="--batch --no-tty --local-user $GPG_KEY"}

sign_deb_repo()
{
	rm -f InRelease Release.gpg &&
	gpg $GPG_OPTS --clearsign -o InRelease Release &&
	gpg $GPG_OPTS --armor --detach-sign --sign -o Release.gpg Release
}

sign_rpm_repo()
{
	rpm --addsign \
		-D "_gpg_name $GPG_KEY" \
		-D "__gpg_sign_cmd /usr/bin/gpg gpg $GPG_OPTS --no-armor -sbo %{__signature_filename} %{__plaintext_filename}" \
		$(find * -name '*.rpm') >/dev/null &&
	createrepo_c -q .
}

if [ -f Release ]; then
	sign_deb_repo || exit
elif [ -n "$(find * -name '*.rpm' -print -quit)" ]; then
	sign_rpm_repo || exit
fi
