# Feature: Page Helpers + Return Page

## Summary

Add one-liner page creation functions (`add_checkout_page()`, `add_express_checkout_page()`) that auto-compose checkout components, register API routes, and add return pages — matching the `add_sign_in_page()` pattern from reflex-clerk-api. Also add a `checkout_return_page()` component and `StripeState.get_session_status()` event handler for post-payment status display.

## User Story

As a Reflex developer
I want to call `stripe.add_checkout_page(app, ...)` with my keys and line items
So that I get a fully working checkout page with return page without composing components manually

## Problem Statement

Developers must manually compose `stripe_provider()`, `ExpressCheckoutBridge.create()`, `embedded_checkout_session()`, wire `register_stripe_api()`, build return pages, and handle session status retrieval. This should be a one-liner per checkout flow.

## Solution Statement

Create `pages.py` with factory functions that receive `rx.App`, compose the appropriate checkout component wrapped in a centered layout, auto-register Stripe API routes, and add both the checkout page and a return page. Add `StripeState.get_session_status()` for server-side session/payment status retrieval on return pages.

## Metadata

| Field            | Value                                                     |
| ---------------- | --------------------------------------------------------- |
| Type             | NEW_CAPABILITY                                            |
| Complexity       | MEDIUM                                                    |
| Systems Affected | pages.py (new), stripe_state.py, __init__.py, tests       |
| Dependencies     | reflex>=0.8.0, stripe>=12.0.0                             |
| Estimated Tasks  | 7                                                         |

---

## UX Design

### Before State

```
Developer code (current — 15+ lines):

    app = rx.App()
    stripe.register_stripe_api(app)

    def checkout():
        return rx.center(
            stripe.embedded_checkout_session(
                publishable_key=os.environ["STRIPE_PUBLISHABLE_KEY"],
                secret_key=os.environ["STRIPE_SECRET_KEY"],
                line_items=[{"price": "price_xxx", "quantity": 1}],
                return_url="/checkout/return",
            ),
            height="100vh",
        )

    def checkout_return():
        return rx.center(rx.text("Payment complete"), height="100vh")

    app.add_page(checkout, route="/checkout")
    app.add_page(checkout_return, route="/checkout/return")
```

### After State

```
Developer code (new — 5 lines):

    app = rx.App()
    stripe.add_checkout_page(
        app,
        line_items=[{"price": "price_xxx", "quantity": 1}],
    )
```

### Interaction Changes

| Location | Before | After | User Impact |
|----------|--------|-------|-------------|
| App setup | 15+ lines manual composition | 1 function call | Checkout in <5 lines |
| Return page | Developer must build from scratch | Auto-added with status display | Working return page out of the box |
| API routes | Manual `register_stripe_api(app)` call | Auto-called by page helpers | One less setup step |
| Session status | No built-in way to check | `StripeState.get_session_status()` on_load | Payment status displayed automatically |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `custom_components/reflex_stripe/stripe_state.py` | all | State to extend with `get_session_status()` |
| P0 | `custom_components/reflex_stripe/embedded_checkout.py` | 187-228 | `embedded_checkout_session()` factory to wrap |
| P0 | `custom_components/reflex_stripe/express_checkout.py` | 166-190 | `ExpressCheckoutBridge.create()` to wrap |
| P0 | `custom_components/reflex_stripe/stripe_provider.py` | 103-153 | `stripe_provider()` factory to wrap |
| P1 | `custom_components/reflex_stripe/__init__.py` | all | Exports to update |
| P1 | `tests/test_import.py` | all | Test pattern to extend |
| P1 | `tests/test_stripe_state.py` | all | State test pattern |
| P2 | `stripe_demo/stripe_demo/stripe_demo.py` | all | Demo to simplify |

**External Documentation:**

| Source | Section | Why Needed |
|--------|---------|------------|
| [Stripe Embedded Checkout Return](https://docs.stripe.com/payments/checkout/custom-success-page?payment-ui=embedded-form) | Custom success page | Return page session retrieval pattern |
| [Stripe confirmPayment return](https://docs.stripe.com/js/payment_intents/confirm_payment) | Return URL params | Express checkout adds `payment_intent`, `payment_intent_client_secret`, `redirect_status` |
| [Reflex Router Attributes](https://reflex.dev/docs/utility-methods/router-attributes/) | `self.router.page.params` | How to read URL query params in State |

---

## Patterns to Mirror

**PAGE_HELPER_PATTERN (from reflex-clerk-api):**

```python
# SOURCE: reflex-clerk-api/custom_components/reflex_clerk_api/pages.py:12-32
# COPY THIS PATTERN:
def add_sign_in_page(
    app: rx.App, publishable_key: str | None = None, route: str = "/sign-in"
) -> None:
    assert route.startswith("/")
    publishable_key = publishable_key or os.environ["CLERK_PUBLISHABLE_KEY"]

    sign_in_page = clerk.clerk_provider(
        rx.center(
            rx.vstack(
                clerk.sign_in(path=route),
                align="center",
                spacing="7",
            ),
            height="100vh",
        ),
        publishable_key=publishable_key,
    )
    app.add_page(sign_in_page, route=route + "/[[...splat]]")
```

**FACTORY_FUNCTION_PATTERN:**

```python
# SOURCE: custom_components/reflex_stripe/embedded_checkout.py:187-228
# COPY THIS PATTERN for parameter handling:
def embedded_checkout_session(
    *children,
    publishable_key: str,
    secret_key: str | None = None,
    line_items: list[dict] | None = None,
    return_url: str = "/checkout/return",
    **props,
) -> rx.Component:
    from .stripe_state import StripeState
    if secret_key:
        StripeState._set_secret_key(secret_key)
    if line_items is not None:
        StripeState._set_checkout_defaults(line_items=line_items, return_url=return_url)
    return EmbeddedCheckoutBridge.create(*children, publishable_key=publishable_key, **props)
```

**STATE_EVENT_HANDLER_PATTERN:**

```python
# SOURCE: custom_components/reflex_stripe/stripe_state.py:171-190
# COPY THIS PATTERN for event handlers:
@rx.event
def handle_payment_success(self, payment_intent_id: str = ""):
    self.payment_status = "succeeded"
    self.error_message = ""

@rx.event
def handle_payment_error(self, error_message: str = ""):
    self.payment_status = "failed"
    self.error_message = error_message
```

**TEST_PATTERN:**

```python
# SOURCE: tests/test_import.py:17-47
# COPY THIS PATTERN for export tests:
def test_all_exports():
    import reflex_stripe
    expected = ["add_checkout_page", "add_express_checkout_page", ...]
    for name in expected:
        assert hasattr(reflex_stripe, name), f"Missing export: {name}"
```

---

## Files to Change

| File | Action | Justification |
|------|--------|---------------|
| `custom_components/reflex_stripe/pages.py` | CREATE | Page helper functions + return page component |
| `custom_components/reflex_stripe/stripe_state.py` | UPDATE | Add `get_session_status()` + `get_payment_status()` event handlers, `customer_email` field |
| `custom_components/reflex_stripe/__init__.py` | UPDATE | Add new exports |
| `tests/test_pages.py` | CREATE | Tests for page helpers |
| `tests/test_import.py` | UPDATE | Add new exports to expected list |
| `tests/test_stripe_state.py` | UPDATE | Add tests for new event handlers |
| `stripe_demo/stripe_demo/stripe_demo.py` | UPDATE | Simplify demo using page helpers |

---

## NOT Building (Scope Limits)

- **Webhook handler** — Fulfillment should use webhooks, not return page. Out of scope per PRD.
- **Custom return page styling** — Return page is functional, not branded. Users can build their own.
- **Subscription return page** — Only `mode='payment'` return flow. Subscriptions deferred.
- **Client-side PaymentIntent retrieval** — Express checkout return uses server-side retrieval, not `stripe.retrievePaymentIntent()` JS call. Simpler and more secure.

---

## Step-by-Step Tasks

### Task 1: UPDATE `custom_components/reflex_stripe/stripe_state.py`

- **ACTION**: Add `customer_email` state var, `get_session_status()` and `get_payment_status()` event handlers
- **IMPLEMENT**:
  1. Add `customer_email: str = ""` instance variable
  2. Add `get_session_status(self)` event handler:
     - Reads `session_id` from `self.router.page.params`
     - If present, calls `client.v1.checkout.sessions.retrieve_async(session_id)`
     - Sets `payment_status` based on `session.status` ("complete" → "succeeded", "open" → "idle", "expired" → "failed")
     - Sets `customer_email` from `session.customer_details.email`
     - Sets `error_message` if status is not "complete"
  3. Add `get_payment_status(self)` event handler:
     - Reads `payment_intent` from `self.router.page.params`
     - If present, calls `client.v1.payment_intents.retrieve_async(payment_intent)`
     - Sets `payment_status` from `intent.status`
     - Sets `error_message` if status is not "succeeded"
  4. Add `reset_payment()` to also reset `customer_email`
- **MIRROR**: `stripe_state.py:171-190` — event handler pattern
- **GOTCHA**: Use `self.router.page.params` (dict), not `self.router.page.query_params`. Both `get_session_status` and `get_payment_status` must handle missing params gracefully (no-op if param absent).
- **GOTCHA**: Session `status` values are `"open"/"complete"/"expired"` — map to `payment_status` field which uses `"idle"/"succeeded"/"failed"`.
- **VALIDATE**: `uv run ruff check custom_components/ && uv run pytest tests/test_stripe_state.py -v`

### Task 2: CREATE `custom_components/reflex_stripe/pages.py`

- **ACTION**: Create page helper module with three functions
- **IMPLEMENT**:
  1. `add_checkout_page(app, publishable_key, secret_key, line_items, route, return_route)`:
     - Signature: `(app: rx.App, publishable_key: str | None = None, secret_key: str | None = None, line_items: list[dict] | None = None, route: str = "/checkout", return_route: str = "/checkout/return") -> None`
     - `assert route.startswith("/")`
     - Read keys from env if None: `os.environ.get("STRIPE_PUBLISHABLE_KEY", "")`, same for secret
     - Auto-call `register_stripe_api(app)` (idempotent — wrap in try/except or check)
     - Compose: `embedded_checkout_session(publishable_key=..., secret_key=..., line_items=..., return_url=return_route)`
     - Wrap in `rx.center(rx.vstack(..., align="center", spacing="4", width="100%", max_width="600px", padding="8"), height="100vh")`
     - Call `app.add_page(component, route=route)`
     - Call `app.add_page(checkout_return_page(), route=return_route, on_load=StripeState.get_session_status)`
  2. `add_express_checkout_page(app, publishable_key, secret_key, amount, currency, route, return_route)`:
     - Signature: `(app: rx.App, publishable_key: str | None = None, secret_key: str | None = None, amount: int = 1099, currency: str = "usd", route: str = "/express-checkout", return_route: str = "/express-checkout/complete") -> None`
     - Same pattern: assert route, read env, register API
     - Compose: `stripe_provider(ExpressCheckoutBridge.create(return_url=return_route), publishable_key=..., secret_key=..., mode="payment", amount=..., currency=...)`
     - Wrap in centered layout
     - Call `app.add_page(component, route=route)`
     - Call `app.add_page(checkout_return_page(), route=return_route, on_load=StripeState.get_payment_status)`
  3. `checkout_return_page()`:
     - Returns an `rx.Component` showing payment status
     - Uses `rx.cond(StripeState.payment_status == "succeeded", success_view, pending_or_error_view)`
     - Success: heading "Payment Successful!", customer email if available, link home
     - Error: heading "Payment Issue", error message, link to retry
     - Loading: spinner + "Checking payment status..."
- **MIRROR**: reflex-clerk-api `pages.py:12-32` for structure
- **IMPORTS**: `import os; import reflex as rx; from .stripe_state import StripeState, register_stripe_api; from .embedded_checkout import embedded_checkout_session; from .stripe_provider import stripe_provider; from .express_checkout import ExpressCheckoutBridge`
- **GOTCHA**: `register_stripe_api` may raise if called twice. Wrap in try/except to make idempotent.
- **GOTCHA**: `on_load` param in `app.add_page()` takes a State event handler reference, not a call.
- **VALIDATE**: `uv run ruff check custom_components/reflex_stripe/pages.py`

### Task 3: UPDATE `custom_components/reflex_stripe/__init__.py`

- **ACTION**: Add page helper exports
- **IMPLEMENT**:
  1. Add import: `from .pages import add_checkout_page, add_express_checkout_page, checkout_return_page`
  2. Add to `__all__`: `"add_checkout_page"`, `"add_express_checkout_page"`, `"checkout_return_page"`
- **MIRROR**: `__init__.py:1-61` — existing import/export pattern
- **VALIDATE**: `uv run python -c "import reflex_stripe; print(reflex_stripe.add_checkout_page)"`

### Task 4: CREATE `tests/test_pages.py`

- **ACTION**: Create tests for page helper functions
- **IMPLEMENT**:
  1. `test_add_checkout_page_callable()` — verify function is importable and callable
  2. `test_add_express_checkout_page_callable()` — same
  3. `test_checkout_return_page_callable()` — verify returns rx.Component
  4. `test_checkout_return_page_returns_component()` — call `checkout_return_page()` and check it returns a component
  5. `test_add_checkout_page_asserts_route()` — verify route must start with "/"
  6. `test_add_express_checkout_page_asserts_route()` — same
- **MIRROR**: `tests/test_import.py:50-94` — test structure
- **GOTCHA**: Cannot fully test `app.add_page()` without a running Reflex app. Test callability and route validation only.
- **VALIDATE**: `uv run pytest tests/test_pages.py -v`

### Task 5: UPDATE `tests/test_import.py`

- **ACTION**: Add new exports to expected list
- **IMPLEMENT**:
  1. Add `"add_checkout_page"`, `"add_express_checkout_page"`, `"checkout_return_page"` to `expected` list in `test_all_exports()`
- **MIRROR**: `tests/test_import.py:17-47` — alphabetical ordering
- **VALIDATE**: `uv run pytest tests/test_import.py -v`

### Task 6: UPDATE `tests/test_stripe_state.py`

- **ACTION**: Add tests for new StripeState event handlers and fields
- **IMPLEMENT**:
  1. `test_customer_email_default()` — verify `customer_email` defaults to `""`
  2. `test_stripe_state_has_get_session_status()` — verify `get_session_status` exists
  3. `test_stripe_state_has_get_payment_status()` — verify `get_payment_status` exists
  4. `test_reset_payment_clears_customer_email()` — verify reset clears the field
- **MIRROR**: `tests/test_stripe_state.py:89-97` — handler existence tests
- **VALIDATE**: `uv run pytest tests/test_stripe_state.py -v`

### Task 7: UPDATE `stripe_demo/stripe_demo/stripe_demo.py`

- **ACTION**: Simplify demo to showcase page helpers alongside manual composition
- **IMPLEMENT**:
  1. Keep existing manual `index()` page as-is (shows explicit composition)
  2. Replace `checkout_complete()` with `stripe.checkout_return_page()` import
  3. Add two page-helper examples at bottom:
     - `stripe.add_checkout_page(app, route="/embedded", return_route="/embedded/return", line_items=[...])`
     - `stripe.add_express_checkout_page(app, route="/express", return_route="/express/complete", amount=1099)`
  4. Keep `stripe.register_stripe_api(app)` (idempotent)
- **MIRROR**: `stripe_demo/stripe_demo/stripe_demo.py:76-79` — app setup pattern
- **VALIDATE**: `uv run ruff check stripe_demo/`

---

## Testing Strategy

### Unit Tests to Write

| Test File | Test Cases | Validates |
|-----------|-----------|-----------|
| `tests/test_pages.py` | callable checks, route assertions, component return | Page helpers |
| `tests/test_stripe_state.py` | handler existence, field defaults, reset | State extensions |
| `tests/test_import.py` | updated export list | Public API completeness |

### Edge Cases Checklist

- [ ] Route not starting with "/" raises AssertionError
- [ ] Missing env vars (STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY) — fallback to empty string
- [ ] `get_session_status()` with no session_id in params — no-op
- [ ] `get_payment_status()` with no payment_intent in params — no-op
- [ ] `register_stripe_api` called multiple times — must not crash
- [ ] Return page with expired session — shows error state
- [ ] Return page with no query params — shows loading/idle state

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

```bash
uv run ruff check custom_components/ tests/ stripe_demo/
```

**EXPECT**: Exit 0, no errors

### Level 2: UNIT_TESTS

```bash
uv run pytest tests/ -v
```

**EXPECT**: All tests pass (existing + new)

### Level 3: FULL_SUITE

```bash
uv run ruff check custom_components/ tests/ stripe_demo/ && uv run pytest tests/ -v
```

**EXPECT**: All pass

### Level 6: MANUAL_VALIDATION

1. `cd stripe_demo && uv run reflex run`
2. Visit `/embedded` — should show embedded checkout
3. Visit `/express` — should show express checkout buttons
4. Complete a test payment — should redirect to return page with status

---

## Acceptance Criteria

- [ ] `stripe.add_checkout_page(app, line_items=[...])` creates checkout at `/checkout` + return at `/checkout/return`
- [ ] `stripe.add_express_checkout_page(app, amount=1099)` creates express checkout at `/express-checkout` + return
- [ ] `checkout_return_page()` displays payment status from query params
- [ ] `StripeState.get_session_status()` reads `session_id` from URL and fetches session status
- [ ] `StripeState.get_payment_status()` reads `payment_intent` from URL and fetches intent status
- [ ] All existing tests still pass (no regressions)
- [ ] New tests pass: `test_pages.py`, updated `test_import.py`, updated `test_stripe_state.py`
- [ ] Demo app works with page helpers

---

## Completion Checklist

- [ ] All 7 tasks completed in order
- [ ] Each task validated after completion
- [ ] Level 1: Lint passes
- [ ] Level 2: All tests pass
- [ ] Level 3: Full suite passes
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `register_stripe_api` crashes on double-call | MED | LOW | Wrap in try/except in page helpers |
| `self.router.page.params` API change in future Reflex | LOW | MED | Pin `reflex>=0.8.0`, test with current version |
| Express checkout return has no `payment_intent` param in test mode | LOW | LOW | `get_payment_status` handles missing param gracefully |
| `app.add_page(component, on_load=...)` syntax changes | LOW | MED | Verify with Reflex docs, test in demo |

---

## Notes

- **Two return flows**: Embedded Checkout returns with `?session_id=cs_test_...`, Express Checkout returns with `?payment_intent=pi_...&payment_intent_client_secret=pi_..._secret_...&redirect_status=succeeded`. The page helpers wire the correct `on_load` handler for each.
- **`register_stripe_api` idempotency**: Page helpers auto-call this so users don't need to. Must handle the case where it's already been called.
- **Stripe session.status mapping**: `"complete"` → `payment_status="succeeded"`, `"open"` → `"idle"`, `"expired"` → `"failed"`.
- **PaymentIntent.status mapping**: `"succeeded"` → `"succeeded"`, `"processing"` → `"processing"`, `"requires_payment_method"` → `"failed"`.
