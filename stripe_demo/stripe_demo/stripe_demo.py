"""reflex-stripe demo application."""

import reflex as rx


class State(rx.State):
    """Base state."""


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("reflex-stripe Demo", size="8"),
            rx.text("Express Checkout and Embedded Checkout coming soon."),
            align="center",
            spacing="4",
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(index, route="/")
