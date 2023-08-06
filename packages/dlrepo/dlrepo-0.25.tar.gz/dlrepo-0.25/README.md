# dlrepo

[![builds.sr.ht status](https://builds.sr.ht/~rjarry/dlrepo.svg)](https://builds.sr.ht/~rjarry/dlrepo)

[dlrepo][hub] is an artifact repository. It supports storing build artifacts
(binary packages, documentation, vm images, container images, etc.) in
a structured file system tree. It exposes an HTTP API to upload files, delete
them, add metadata, etc. [dlrepo][hub] does not use an external database. It
does de-duplication of artifacts by the use of file system hard links.

[hub]: https://sr.ht/~rjarry/dlrepo/

## installation

```
pip install dlrepo
```

## development quickstart

```
sudo apt install libldap2-dev libsasl2-dev python3-dev python3-pip python3-venv sassc
git clone https://git.sr.ht/~rjarry/dlrepo
cd dlrepo
make lint tests
make run
```

## documentation

* [dlrepo.7](https://git.sr.ht/~rjarry/dlrepo/tree/main/item/docs/dlrepo.7.scdoc)
* [dlrepo-cli.1](https://git.sr.ht/~rjarry/dlrepo/tree/main/item/docs/dlrepo-cli.1.scdoc)
* [dlrepo-config.5](https://git.sr.ht/~rjarry/dlrepo/tree/main/item/docs/dlrepo-config.5.scdoc)
* [dlrepo-acls.5](https://git.sr.ht/~rjarry/dlrepo/tree/main/item/docs/dlrepo-acls.5.scdoc)
* [dlrepo-api.7](https://git.sr.ht/~rjarry/dlrepo/tree/main/item/docs/dlrepo-api.7.scdoc)
* [dlrepo-layout.7](https://git.sr.ht/~rjarry/dlrepo/tree/main/item/docs/dlrepo-layout.7.scdoc)

## contributing

Anyone can contribute to dlrepo:

* Clone the repository.
* Patch the code.
* Make some tests.
* Ensure that your code is properly formatted with black (`make format`).
* Ensure that the linters are happy (`make lint`).
* Ensure that everything works as expected.
* Ensure that you did not break anything.
* If applicable, update unit tests.
* If adding a new feature, please consider adding new tests.
* Do not forget to update the docs.

Once you are happy with your work, you can create a commit (or several
commits). Follow these general rules:

* Limit the first line (title) of the commit message to 60 characters.
* Use a short prefix for the commit title for readability with `git log --oneline`.
* Use the body of the commit message to actually explain what your patch does
  and why it is useful.
* Address only one issue/topic per commit.
* If you are fixing a ticket, use appropriate
  [commit trailers](https://man.sr.ht/git.sr.ht/#referencing-tickets-in-git-commit-messages).
* If you are fixing a regression introduced by another commit, add a `Fixes:`
  trailer with the commit id and its title.

There is a great reference for commit messages in the
[Linux kernel documentation](https://www.kernel.org/doc/html/latest/process/submitting-patches.html#describe-your-changes).

Before sending the patch, you should configure your local clone with sane
defaults:

```
git config format.subjectPrefix "PATCH dlrepo"
git config sendemail.to "~rjarry/dlrepo@lists.sr.ht"
```

And send the patch to the mailing list:

```
git sendemail --annotate -1
```

Wait for feedback. Address comments and amend changes to your original commit.
Then you should send a v2:

```
git sendemail --in-reply-to=$first_message_id --annotate -v2 -1
```

Once the maintainer is happy with your patch, they will apply it and push it.

## resources

* Browse [source code](https://git.sr.ht/~rjarry/dlrepo)
* Submit patches & questions to
  [~rjarry/dlrepo@lists.sr.ht](https://lists.sr.ht/~rjarry/dlrepo)
* File or browse [tickets](https://todo.sr.ht/~rjarry/dlrepo)
