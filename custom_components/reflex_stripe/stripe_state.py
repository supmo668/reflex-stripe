"""StripeState backend state and API endpoint for PaymentIntent management."""

import logging
import os
from typing import ClassVar

import reflex as rx
import stripe as stripe_lib
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

logger = logging.getLogger(__name__)


class StripeState(rx.State):
    """Backend state for Stripe payment management.

    Manages PaymentIntent creation via the Stripe Python SDK,
    tracks payment status, and stores client_secret for frontend use.

    ClassVars (_secret_key, _stripe_client, etc.) are shared across all
    sessions and set once at app initialization via stripe_provider() factory.
    """

    # Per-instance state (synced to frontend via WebSocket)
    client_secret: str = ""
    """The client_secret from the current PaymentIntent."""

    payment_status: str = "idle"
    """Payment lifecycle status: 'idle', 'requires_payment_method',
    'processing', 'succeeded', 'failed', etc."""

    error_message: str = ""
    """Last payment error message, if any."""

    # ClassVar — shared across all instances, not persisted per session.
    # NOTE: RUF012 is ignored project-wide in pyproject.toml for ClassVar annotations.
    _secret_key: ClassVar[str | None] = None
    _stripe_client: ClassVar[stripe_lib.StripeClient | None] = None
    _default_amount: ClassVar[int] = 0
    _default_currency: ClassVar[str] = "usd"
    _return_url: ClassVar[str] = ""

    @classmethod
    def _set_secret_key(cls, secret_key: str) -> None:
        """Store Stripe secret key. Called by stripe_provider() factory."""
        if not secret_key:
            raise ValueError("Stripe secret_key must not be empty")
        cls._secret_key = secret_key
        cls._stripe_client = None  # Force re-initialization

    @classmethod
    def _set_defaults(
        cls,
        amount: int = 0,
        currency: str = "usd",
        return_url: str = "",
    ) -> None:
        """Store default payment parameters for the API endpoint."""
        cls._default_amount = amount
        cls._default_currency = currency
        cls._return_url = return_url

    @classmethod
    def _get_client(cls) -> stripe_lib.StripeClient:
        """Get or create the Stripe API client (lazy initialization)."""
        if cls._stripe_client is None:
            key = cls._secret_key or os.environ.get("STRIPE_SECRET_KEY", "")
            if not key:
                raise ValueError(
                    "STRIPE_SECRET_KEY must be passed to stripe_provider() "
                    "or set as an environment variable"
                )
            cls._stripe_client = stripe_lib.StripeClient(
                key, http_client=stripe_lib.HTTPXClient()
            )
        return cls._stripe_client

    @rx.event(background=True)
    async def create_payment_intent(
        self, amount: int | None = None, currency: str | None = None
    ):
        """Create a PaymentIntent and store the client_secret in state.

        Can be called directly as a Reflex event for programmatic use.
        The JS bridge uses the API endpoint instead (synchronous response needed).
        """
        amt = amount or self._default_amount
        cur = currency or self._default_currency
        if not amt:
            async with self:
                self.error_message = "Amount is required"
                self.payment_status = "failed"
            return

        try:
            client = self._get_client()
            intent = await client.v1.payment_intents.create_async({
                "amount": amt,
                "currency": cur,
                "automatic_payment_methods": {"enabled": True},
            })
            async with self:
                self.client_secret = intent.client_secret
                self.payment_status = intent.status
                self.error_message = ""
            logger.info("PaymentIntent created: %s", intent.id)
        except Exception as e:
            logger.error("Failed to create PaymentIntent: %s", e)
            async with self:
                self.error_message = str(e)
                self.payment_status = "failed"

    @rx.event
    def handle_payment_success(self, payment_intent_id: str = ""):
        """Called from JS bridge after successful confirmPayment."""
        self.payment_status = "succeeded"
        self.error_message = ""
        logger.info("Payment succeeded: %s", payment_intent_id)

    @rx.event
    def handle_payment_error(self, error_message: str = ""):
        """Called from JS bridge on payment failure."""
        self.payment_status = "failed"
        self.error_message = error_message
        logger.warning("Payment failed: %s", error_message)

    @rx.event
    def reset_payment(self):
        """Reset payment state for a new transaction."""
        self.client_secret = ""
        self.payment_status = "idle"
        self.error_message = ""


async def _create_payment_intent_endpoint(request: Request) -> JSONResponse:
    """Starlette endpoint for creating PaymentIntents.

    Called by ExpressCheckoutBridge via fetch() during the onConfirm flow.
    Returns client_secret as JSON for immediate use in stripe.confirmPayment().
    """
    try:
        client = StripeState._get_client()
        intent = await client.v1.payment_intents.create_async({
            "amount": StripeState._default_amount,
            "currency": StripeState._default_currency,
            "automatic_payment_methods": {"enabled": True},
        })
        return JSONResponse({"client_secret": intent.client_secret})
    except Exception as e:
        logger.error("API: Failed to create PaymentIntent: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)


def get_stripe_api_routes() -> list[Route]:
    """Create Starlette routes for Stripe API endpoints.

    Returns:
        List of Route objects for mounting on a Starlette app.
    """
    return [
        Route(
            "/api/stripe/create-payment-intent",
            _create_payment_intent_endpoint,
            methods=["POST"],
        ),
    ]


def register_stripe_api(app) -> None:
    """Register Stripe API routes on the Reflex app.

    Call this in your app setup after creating the rx.App::

        import reflex_stripe as stripe
        app = rx.App()
        stripe.register_stripe_api(app)

    Args:
        app: The Reflex app (rx.App) instance.
    """
    starlette_app = getattr(app, "_api", None) or getattr(app, "api", None)
    if starlette_app is None:
        raise RuntimeError(
            "Cannot register Stripe API: app has no Starlette backend. "
            "Make sure rx.App() is initialized before calling register_stripe_api()."
        )
    for route in get_stripe_api_routes():
        starlette_app.add_route(
            route.path,
            route.endpoint,
            methods=route.methods,
        )
