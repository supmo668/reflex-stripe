import json

import reflex as rx
from reflex.utils.imports import ImportVar

# ``loadStripe`` comes from the side-effect-free entry of the pinned
# ``@stripe/stripe-js`` package. The default entry injects the Stripe.js
# ``<script>`` as soon as the module is imported; the pure entry does nothing
# until ``loadStripe`` is called.
#
# Reflex derives two things from an import-dict key: the npm spec it installs
# (the key as written) and the JS import specifier (the key with ``@version``
# stripped). A key cannot carry both a version and a subpath, so they are
# declared separately:
#
#   * the exact spec, install-only: ``"<name>@<X.Y.Z>": [INSTALL_ONLY]``
#     (what ``lib_dependencies`` does), which renders no JS import;
#   * the entry file, import-only: ``STRIPE_JS_PURE: [LOAD_STRIPE]`` with
#     ``install=False``, so Reflex never hands the versionless name to the
#     package manager.
#
# Do NOT put the entry on the versioned key as an ImportVar ``package_path``:
# merged with a ``lib_dependencies`` entry for the same key, Reflex then also
# renders a bare ``import "@stripe/stripe-js"`` of the default entry.
#
# The specifier names the file (``pure/index.mjs``), not the directory
# (``pure``): the package has no ``exports`` map, and Node's native ES module
# loader (which evaluates page modules when routes are prerendered) refuses
# directory imports.
STRIPE_JS_PURE = "@stripe/stripe-js/pure/index.mjs"
INSTALL_ONLY = ImportVar(tag=None, render=False)
LOAD_STRIPE = ImportVar(tag="loadStripe", install=False)

# Module-level, memoised ``loadStripe``. Nothing runs when the module is
# evaluated: Stripe.js is requested on the first ``getStripePromise(key)``
# call, which the components make while rendering. Later calls with the same
# key return the SAME promise object (react-stripe-js rejects a changing
# ``stripe`` prop). The string is identical for every component and key, so
# Reflex's per-page custom-code deduplication emits it once.
STRIPE_LOADER_JS = """
const stripePromiseCache = new Map();
function getStripePromise(publishableKey) {
  let promise = stripePromiseCache.get(publishableKey);
  if (!promise) {
    promise = loadStripe(publishableKey);
    stripePromiseCache.set(publishableKey, promise);
  }
  return promise;
}
"""


def stripe_promise_js(publishable_key: str) -> str:
    """JS expression for the memoised Stripe promise of ``publishable_key``.

    Evaluate it at render time only (inside a component body or a JSX prop).
    """
    return f"getStripePromise({json.dumps(publishable_key)})"


class StripeBase(rx.Component):
    """Base component for all Stripe React component wrappers."""

    # The React library to wrap.
    library = "@stripe/react-stripe-js@7.0.0"

    # Additional npm packages required.
    lib_dependencies: list[str] = ["@stripe/stripe-js@10.0.0"]
