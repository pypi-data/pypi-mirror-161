import json
import logging
from asyncio.log import logger

import requests
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse

from config import settings
from ob_dj_store.core.stores.models import Order, Payment

User = get_user_model()
logger = logging.getLogger(__name__)


class TapException(Exception):
    pass


def initiate_payment(
    source: str,
    user: User,
    order: Order,
    payment: Payment,
    currency_code: str,
):
    """Initiate payment URL and return charge_id, payment_url and response"""

    redirect_path = reverse(f"tap_gateway:taptransaction-get")
    callback_path = reverse(f"tap_gateway:taptransaction-callback")
    redirect_url = f"{settings.WEBSITE_URL}{redirect_path}"
    callback_url = f"{settings.WEBSITE_URL}{callback_path}"

    payload = {
        "amount": "%.3f" % payment.amount,
        "currency": currency_code,
        "source": {"id": source},
        "customer": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
        "post": {"url": callback_url},
        "redirect": {"url": redirect_url},
    }

    url = "/charges/"
    method = "POST"
    if not settings.TAP_SECRET_KEY:
        raise ValueError("TAP Secret is missing from settings")
    tap_secret_key = settings.TAP_SECRET_KEY
    headers = {
        "authorization": f"Bearer {tap_secret_key}",
        "content-type": "application/json",
        "cache-control": "no-cache",
    }
    payload = json.dumps(payload, cls=DjangoJSONEncoder)
    response = requests.request(
        url=f"{settings.TAP_API_URL}{url}", method=method, data=payload, headers=headers
    )
    tap_response = response.json()
    payment_url = tap_response.get("transaction").get("url")
    charge_id = tap_response.get("id")
    if not payment_url or not charge_id:
        # TODO: How does this issue occur and is this the best way to handle it?
        logger.error(
            f"Failed to create charge request no payment_url or charge_id returned."
        )
        raise TapException(payload)

    status = tap_response.get("status")
    source = tap_response.get("source").get("id") if source else ""

    return {
        "charge_id": charge_id,
        "payment_url": payment_url,
        "init_response": tap_response,
        "source": source,
        "status": status,
    }
