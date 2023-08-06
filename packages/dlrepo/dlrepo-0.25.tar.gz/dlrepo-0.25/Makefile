# Copyright (c) 2021 Julien Floret
# Copyright (c) 2021 Robin Jarry
# SPDX-License-Identifier: BSD-3-Clause

PYTHON = python3
PIP = $(PYTHON) -m pip
VIRTUALENV = $(PYTHON) -m venv
VENV = .venv
in_venv = . $(VENV)/bin/activate &&

.PHONY: all
all: lint-full

$(VENV)/bin/activate:
	$(VIRTUALENV) $(VENV)

$(VENV)/.stamp: $(VENV)/bin/activate requirements-dev.txt setup.py
	$(in_venv) $(PIP) install -U -r requirements-dev.txt
	@touch $@

PY_FILES = $(shell git ls-files -- '*.py' 2>/dev/null || find * -name '*.py')
PY_FILES += dlrepo-cli
J ?= $(shell nproc)

.PHONY: lint
lint: $(VENV)/.stamp
	@echo "[black]"
	@$(in_venv) $(PYTHON) -m black -q -t py36 --diff --check $(PY_FILES) || \
		{ echo "Use 'make format' to fix the problems."; exit 1; }
	@echo "[isort]"
	@$(in_venv) $(PYTHON) -m isort -j$(J) --diff --check-only $(PY_FILES) || \
		{ echo "Use 'make format' to fix the problems."; exit 1; }
	@echo "[flake8]"
	@$(in_venv) $(PYTHON) -m flake8 -j$(J) $(PY_FILES)
	@echo "[pylint]"
	@$(in_venv) $(PYTHON) -m pylint $(PY_FILES)

.PHONY: format
format: $(VENV)/.stamp
	@echo "[isort]"
	@$(in_venv) $(PYTHON) -m isort -j$(J) $(PY_FILES)
	@echo "[black]"
	@$(in_venv) $(PYTHON) -m black -q -t py36 $(PY_FILES)

.PHONY: tests
tests: $(VENV)/.stamp
	@$(in_venv) $(PYTHON) -m pytest -v

DLREPO_AUTH_DISABLED ?= 1
DLREPO_ROOT_DIR ?= data
DLREPO_LOG_LEVEL ?= INFO
dlrepo_vars = $(filter DLREPO_%,$(.VARIABLES))
run_env = $(foreach var,$(dlrepo_vars),$(var)=$($(var)))

.PHONY: run
run: $(VENV)/.stamp dlrepo/static/dlrepo.css
	$(in_venv) $(run_env) $(PYTHON) -m dlrepo

.PHONY: css
css: dlrepo/static/dlrepo.css
	@:

dlrepo/static/dlrepo.css: $(wildcard scss/*.scss)
	@mkdir -p $(@D)
	sassc -t compact scss/main.scss $@

.PHONY: watch-css
watch-css: dlrepo/static/dlrepo.css
	while inotifywait -q -e modify scss; do $(MAKE) --no-print-directory css; done

sysconfig = /etc
prefix = /usr/local
systemd_units = $(prefix)/lib/systemd/system

$(destdir)$(systemd_units)/%: etc/%
	install -m 644 -DTC $< $@

$(destdir)$(sysconfig)/default/dlrepo: etc/default
	install -m 644 -DTC $< $@

.PHONY: install_python
install_python:
	$(PYTHON) setup.py install --prefix=$(prefix) $(addprefix --root=,$(destdir))

$(destdir)$(prefix)/share/doc/dlrepo/examples/nginx.conf: etc/nginx.conf
	install -m 644 -DTC $< $@

.PHONY: install_extras
install_extras: $(destdir)$(prefix)/share/doc/dlrepo/examples/nginx.conf

.PHONY: install_services
install_services: $(destdir)$(sysconfig)/default/dlrepo
install_services: $(destdir)$(systemd_units)/dlrepo.socket
install_services: $(destdir)$(systemd_units)/dlrepo.service

docs/%: docs/%.scdoc
	scdoc < $< > $@

man_src = $(wildcard docs/*.scdoc)

.PHONY: man
man: $(man_src:.scdoc=)
	@:

.PHONY: install_man
install_man:
	@:

define install_man_rule
$(destdir)$(prefix)/share/man/man$2/$1.$2: docs/$1.$2
	install -m 644 -DTC $$< $$@

install_man: $(destdir)$(prefix)/share/man/man$2/$1.$2
endef

man_names = $(notdir $(man_src:.scdoc=))
$(foreach m,$(man_names),\
	$(eval $(call install_man_rule,$(basename $(m)),$(subst .,,$(suffix $(m))))))

.PHONY: install
install: install_extras install_python install_services install_man
	mkdir -p $(destdir)/var/lib/dlrepo
	chown dlrepo:dlrepo $(destdir)/var/lib/dlrepo
