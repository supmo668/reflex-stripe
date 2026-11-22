"""Every npm spec this package hands to Reflex is an EXACT version.

Reflex runs `bun add <spec>` for each library a component imports. A bare name
("@stripe/stripe-js") installs whatever is latest at build time and writes a
caret spec; that is how stripe-js 10 / react-stripe-js 7 (majors published the
evening before) reached a production checkout unreviewed on 2026-10-02. Consumer
builds now install frozen from a lockfile, where a bare spec instead turns every
upstream release into a failed build. Either way the version must be declared.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "custom_components" / "reflex_stripe"
EXACT = re.compile(r"^@stripe/(react-)?stripe-js@\d+\.\d+\.\d+$")
# The ONE permitted spec without a version: the side-effect-free entry file of
# @stripe/stripe-js, used as a JS import specifier only. Reflex cannot express
# "install name@X.Y.Z, import name/subpath" in a single key (it strips
# everything after the last "@" to build the specifier), so the package is
# installed through its exact spec and this entry is declared import-only
# (``install=False``; asserted below and per component in
# test_lazy_stripe_load.py). It is matched literally, not by a pattern: any
# other subpath, or this one with a version or range attached, still fails.
PURE_ENTRY = "@stripe/stripe-js/pure/index.mjs"
# Any @stripe/* npm spec used as code (dict key, library=, lib_dependencies,
# constant), with or without a version or subpath — docstring mentions are
# wrapped in ``double backticks`` and skipped.
SPEC = re.compile(r'"(@stripe/(?:react-)?stripe-js[^"]*)"')
DOC_CODE = re.compile(r"``.*?``", re.DOTALL)


def _specs() -> list[tuple[str, str]]:
    out = []
    for p in sorted(SRC.glob("*.py")):
        for spec in SPEC.findall(DOC_CODE.sub("", p.read_text())):
            out.append((p.name, spec))
    return out


def test_specs_were_found() -> None:
    """Guard against the scan silently matching nothing."""
    assert len(_specs()) >= 8


@pytest.mark.parametrize(("file", "spec"), _specs())
def test_every_stripe_spec_is_exact(file: str, spec: str) -> None:
    if spec == PURE_ENTRY:
        return
    assert EXACT.match(spec), f"{file}: {spec!r} is not an exact version (name@X.Y.Z)"


def test_pure_entry_is_declared_once_and_import_only() -> None:
    """The versionless entry is safe only while Reflex never installs it."""
    from reflex_stripe import base

    assert [f for f, spec in _specs() if spec == PURE_ENTRY] == ["base.py"]
    assert base.STRIPE_JS_PURE == PURE_ENTRY
    assert base.LOAD_STRIPE.install is False
    # ...and the package it belongs to is installed from an exact spec.
    assert any(spec.startswith("@stripe/stripe-js@") for _, spec in _specs())


def test_all_sites_agree_on_one_version_per_package() -> None:
    versions: dict[str, set[str]] = {}
    for _, spec in _specs():
        if spec == PURE_ENTRY:
            continue
        name, _, ver = spec.rpartition("@")
        versions.setdefault(name, set()).add(ver)
    assert all(len(v) == 1 for v in versions.values()), versions
