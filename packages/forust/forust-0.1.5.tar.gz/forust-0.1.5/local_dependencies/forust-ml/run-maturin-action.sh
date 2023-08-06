#!/bin/bash
set -e
echo "::group::Install Rust"
which rustup > /dev/null || curl --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
export PATH="$HOME/.cargo/bin:$PATH"
rustup override set stable
rustup component add llvm-tools-preview || true
echo "::endgroup::"
export PATH="$PATH:/opt/python/cp36-cp36m/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp38-cp38/bin:/opt/python/cp39-cp39/bin"
echo "::group::Install maturin"
curl -L https://github.com/PyO3/maturin/releases/download/v0.12.20/maturin-x86_64-unknown-linux-musl.tar.gz | tar -xz -C /usr/local/bin
maturin --version || true
which patchelf > /dev/null || python3 -m pip install patchelf
echo "::endgroup::"
echo "::group::Install Rust target"
if [[ ! -d $(rustc --print target-libdir --target x86_64-unknown-linux-gnu) ]]; then rustup target add x86_64-unknown-linux-gnu; fi
echo "::endgroup::"
maturin publish --username jinlow --password WasThisAnother214 --interpreter python3.9 --skip-existing --manifest-path py-forust/Cargo.toml --target x86_64-unknown-linux-gnu