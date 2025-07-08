TARGET ?= x86_64-pc-windows-gnu

build-rust:
	cargo build --release --target=$(TARGET)

windows: build-rust
	cp -v target/$(TARGET)/release/iso2god.dll src/iso2god/resources/iso2god-x86_64-windows.dll

linux:
	make TARGET=x86_64-unknown-linux-gnu build-rust
	cp -v target/x86_64-unknown-linux-gnu/release/libiso2god.so src/iso2god/resources/iso2god-x86_64-linux.so

android:
	make TARGET=aarch64-linux-android build-rust
	cp -v target/aarch64-linux-android/release/libiso2god.so src/iso2god/resources/iso2god-aarch64-android.so

run:
	briefcase.exe run windows

python-build:
	briefcase.exe create
	briefcase.exe build

.PHONY: build
build: clean build-rust python-build

package:
	briefcase.exe package

clean:
	rm -rf build
	rm -rf target
