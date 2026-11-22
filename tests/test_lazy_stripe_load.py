"""Stripe.js is requested on first render, never when a page module is imported.

The default entry of ``@stripe/stripe-js`` injects the Stripe.js ``<script>`` as
an import side effect, and a module-level ``loadStripe(key)`` runs as soon as
the bundler evaluates the module. Reflex may place a component's module code in
a chunk shared with pages that never render it, so either one makes every page
fetch Stripe.js. These tests pin the replacement: the side-effect-free entry
plus one memoised, render-time getter.
"""

from __future__ import annotations

import re
import shutil
import subprocess

import pytest
import reflex as rx
import reflex_stripe as stripe
from reflex.compiler.utils import compile_imports

KEY = "pk_test_dummy"
PURE_ENTRY = "@stripe/stripe-js/pure/index.mjs"
GETTER_CALL = f'getStripePromise("{KEY}")'
EXACT = re.compile(r"^@stripe/(react-)?stripe-js@\d+\.\d+\.\d+$")


def _guarded(key: str = KEY) -> rx.Component:
    return stripe.EmbeddedCheckoutProvider.create(publishable_key=key, client_secret="")


def _bridge(key: str = KEY) -> rx.Component:
    return stripe.EmbeddedCheckoutBridge.create(publishable_key=key)


def _provider(key: str = KEY) -> rx.Component:
    return stripe.StripeProvider.create(
        stripe.ExpressCheckoutBridge.create(),
        stripe.ExpressCheckoutElement.create(),
        publishable_key=key,
        mode="payment",
        amount=1099,
        currency="usd",
    )


BUILDERS = [_guarded, _bridge, _provider]
ids = [b.__name__.lstrip("_") for b in BUILDERS]


def _code(component: rx.Component) -> list[str]:
    return list(component._get_all_custom_code())


def _js_imports(component: rx.Component) -> dict[str, list[str]]:
    """The JS import statements Reflex renders: specifier -> named imports."""
    return {d["lib"]: d["rest"] for d in compile_imports(component._get_all_imports())}


def _installed(component: rx.Component) -> set[str]:
    """The npm specs Reflex hands to the package manager (its own filter)."""
    return {
        lib
        for lib, tags in component._get_all_imports().items()
        if lib.startswith("@stripe/") and any(tag.install for tag in tags)
    }


# --------------------------------------------------------------- imports


@pytest.mark.parametrize("build", BUILDERS, ids=ids)
def test_load_stripe_comes_from_the_pure_entry(build) -> None:
    js = _js_imports(build())
    assert js.get(PURE_ENTRY) == ["loadStripe"]


@pytest.mark.parametrize("build", BUILDERS, ids=ids)
def test_default_entry_is_never_imported(build) -> None:
    """Neither ``import {loadStripe} from "@stripe/stripe-js"`` nor a bare
    ``import "@stripe/stripe-js"`` (Reflex renders one for a key whose default
    path has no rendered names)."""
    assert "@stripe/stripe-js" not in _js_imports(build())


@pytest.mark.parametrize("build", BUILDERS, ids=ids)
def test_pure_entry_is_import_only_and_installs_stay_exact(build) -> None:
    """The versionless entry specifier must never reach the package manager;
    what does is exactly the two pinned specs."""
    installed = _installed(build())
    assert PURE_ENTRY not in installed
    assert all(EXACT.match(spec) for spec in installed), installed
    assert {spec.rpartition("@")[0] for spec in installed} == {
        "@stripe/stripe-js",
        "@stripe/react-stripe-js",
    }


# ----------------------------------------------------------- custom code


@pytest.mark.parametrize("build", BUILDERS, ids=ids)
def test_no_top_level_load_stripe_call(build) -> None:
    """``loadStripe(`` may appear only inside a function body (indented)."""
    for block in _code(build()):
        for line in block.splitlines():
            if "loadStripe(" in line:
                assert line.startswith((" ", "\t")), f"top-level call: {line!r}"
    assert not re.search(r"const stripePromise\b", "\n".join(_code(build())))


@pytest.mark.parametrize("build", BUILDERS, ids=ids)
def test_memoised_getter_is_emitted_once(build) -> None:
    code = "\n".join(_code(build()))
    assert code.count("function getStripePromise(") == 1
    assert code.count("loadStripe(") == 1


def test_guarded_checkout_calls_getter_at_render_after_the_guard() -> None:
    code = "\n".join(_code(_guarded()))
    component = code.index("function GuardedEmbeddedCheckout(")
    guard = code.index("if (!clientSecret)", component)
    call = code.index(f"stripe={{{GETTER_CALL}}}", component)
    assert component < guard < call


def test_bridge_calls_getter_at_render() -> None:
    code = "\n".join(_code(_bridge()))
    component = code.index("function EmbeddedCheckoutBridge(")
    assert code.index(f"stripe={{{GETTER_CALL}}}") > component


def test_stripe_provider_passes_getter_call_as_stripe_prop() -> None:
    """<Elements> is rendered by Reflex itself, so the call is the JSX prop
    expression: evaluated when the element renders, not at module scope."""
    props = _provider().render()["props"]
    assert f"stripe:{GETTER_CALL}" in props


def test_same_key_components_share_one_getter_and_one_expression() -> None:
    """Several components on one page: identical module code (so Reflex's
    custom-code dedup keeps one copy) and the same getter call (so the
    module-level cache hands every provider the same promise)."""
    assert _code(_guarded()) == _code(_guarded())
    page = rx.fragment(_guarded(), _bridge(), _provider(), _guarded())
    code = "\n".join(_code(page))
    assert code.count("function getStripePromise(") == 1
    assert code.count("new Map()") == 1
    assert code.count("loadStripe(") == 1
    assert code.count(GETTER_CALL) == 2  # guarded (deduplicated) + bridge
    assert f"stripe:{GETTER_CALL}" in _provider().render()["props"]


def test_two_keys_share_the_getter_but_not_the_promise() -> None:
    page = rx.fragment(_guarded("pk_test_a"), _bridge("pk_test_b"))
    code = "\n".join(_code(page))
    assert code.count("function getStripePromise(") == 1
    assert 'getStripePromise("pk_test_a")' in code
    assert 'getStripePromise("pk_test_b")' in code


def test_publishable_key_is_emitted_as_a_js_string_literal() -> None:
    code = "\n".join(_code(_guarded('pk_"quoted')))
    assert 'getStripePromise("pk_\\"quoted")' in code


# ------------------------------------------------------ missing-key guard


@pytest.mark.parametrize("build", [_guarded, _bridge], ids=["guarded", "bridge"])
def test_missing_key_renders_guard_and_never_loads(build) -> None:
    code = "\n".join(_code(build("")))
    assert 'data-stripe-error="Missing publishable key"' in code
    assert "loadStripe(" not in code
    assert "getStripePromise" not in code
    assert "@stripe/stripe-js" not in _js_imports(build(""))


def test_missing_key_stripe_provider_passes_null_and_never_loads() -> None:
    provider = stripe.StripeProvider.create(publishable_key="")
    assert _code(provider) == []
    assert "stripe:null" in provider.render()["props"]
    assert "@stripe/stripe-js" not in _js_imports(provider)


# ------------------------------------------------------------ node check

NODE = shutil.which("node")

HARNESS = """
const calls = [];
const loadStripe = (key) => { calls.push(key); return Promise.resolve({ key }); };
%s
const assert = (ok, msg) => { if (!ok) { console.error("FAIL: " + msg); process.exit(1); } };
assert(calls.length === 0, "loadStripe ran at module evaluation: " + calls);
assert(typeof getStripePromise === "function", "no getStripePromise");
const a = getStripePromise("pk_a");
assert(calls.length === 1, "first use must load once");
assert(getStripePromise("pk_a") === a, "same key must return the same promise");
assert(getStripePromise("pk_a") === a && calls.length === 1, "repeat use reloaded");
const b = getStripePromise("pk_b");
assert(b !== a && calls.length === 2, "one load per publishable key");
assert(calls.join() === "pk_a,pk_b", "wrong keys: " + calls);
console.log("ok");
"""


@pytest.mark.skipif(NODE is None, reason="node is not on PATH")
@pytest.mark.parametrize("build", BUILDERS, ids=ids)
def test_emitted_module_code_loads_lazily_and_once_under_node(build) -> None:
    """Evaluate the emitted module-level code (everything except the JSX
    component bodies) with a counting ``loadStripe`` stub."""
    module_code = [b for b in _code(build()) if "return (" not in b]
    assert NODE is not None
    proc = subprocess.run(
        [NODE, "--input-type=module", "-"],
        input=HARNESS % "\n".join(module_code),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip() == "ok"
