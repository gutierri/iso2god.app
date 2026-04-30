ARCH ?= x86_64
OST ?= linux

ifeq ($(OST),windows)
	LIB_NAME = iso2god
	LIB_SUFFIX = dll
	TARGET_SUFFIX = pc-$(OST)-gnu
else
	LIB_NAME = libiso2god
	LIB_SUFFIX = so
	TARGET_SUFFIX = unknown-$(OST)-gnu
endif

TARGET ?= $(ARCH)-$(TARGET_SUFFIX)
PYVENV := .venv
PIP := $(PYVENV)/bin/pip
PY := $(PYVENV)/bin/python

.PHONY: all
all: clean package

.PHONY: rust
rust:
	cargo build --release --target=$(TARGET)
	mkdir -p src/iso2god/resources
	cp -v \
		target/$(TARGET)/release/$(LIB_NAME).$(LIB_SUFFIX) \
		src/iso2god/resources/iso2god-$(ARCH)-$(OST).$(LIB_SUFFIX)

.PHONY: python
python:
	briefcase build $(OST)

.PHONY: build
build: rust python

.PHONY: package
package: build
	briefcase package $(PACKAGE_ARGS)

.PHONY: clean
clean:
	rm -rf build/ target/ .venv
	find src -type f \( -name "*.so" -o -name "*.dll" \) -delete
