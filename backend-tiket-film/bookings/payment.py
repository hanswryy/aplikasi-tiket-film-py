from collections.abc import Mapping
import hashlib
import hmac
from typing import Any

import midtransclient
from flask import current_app


class PaymentConfigurationError(RuntimeError):
    """Raised when Midtrans credentials are not configured."""


class PaymentGatewayError(RuntimeError):
    """Raised when Midtrans rejects or cannot process a request."""


def _client() -> midtransclient.Snap:
    server_key = current_app.config.get("MIDTRANS_SERVER_KEY")
    client_key = current_app.config.get("MIDTRANS_CLIENT_KEY")
    if not server_key or not client_key:
        raise PaymentConfigurationError(
            "MIDTRANS_SERVER_KEY and MIDTRANS_CLIENT_KEY must be configured"
        )
    return midtransclient.Snap(
        is_production=current_app.config["MIDTRANS_IS_PRODUCTION"],
        server_key=server_key,
        client_key=client_key,
    )


def create_transaction(booking: Any) -> Mapping[str, Any]:
    try:
        transaction = _client().create_transaction(
            {
                "transaction_details": {
                    "order_id": booking.id,
                    "gross_amount": round(booking.total_amount),
                },
                "item_details": [
                    {
                        "id": booking.showtime.movie_id,
                        "price": round(booking.total_amount),
                        "quantity": 1,
                        "name": booking.showtime.movie.title,
                    }
                ],
            }
        )
    except Exception as error:
        raise PaymentGatewayError("Unable to create Midtrans transaction") from error
    if not transaction.get("token") or not transaction.get("redirect_url"):
        raise PaymentGatewayError("Midtrans returned an incomplete transaction")
    return transaction


def verify_notification(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    server_key = current_app.config.get("MIDTRANS_SERVER_KEY")
    if not server_key:
        raise PaymentConfigurationError("MIDTRANS_SERVER_KEY must be configured")
    required = (
        "order_id",
        "status_code",
        "gross_amount",
        "signature_key",
        "transaction_status",
    )
    if any(not payload.get(field) for field in required):
        raise PaymentGatewayError("Midtrans notification is missing required fields")
    expected_signature = hashlib.sha512(
        (
            f"{payload['order_id']}{payload['status_code']}"
            f"{payload['gross_amount']}{server_key}"
        ).encode("utf-8")
    ).hexdigest()
    if not hmac.compare_digest(str(payload["signature_key"]), expected_signature):
        raise PaymentGatewayError("Invalid Midtrans notification signature")
    return payload
