import base64
import hashlib
import hmac
import json

import requests
from django.conf import settings

SIGNED_FIELD_NAMES = 'total_amount,transaction_uuid,product_code'


def _sign(message: str) -> str:
    digest = hmac.new(
        settings.ESEWA_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode('utf-8')


def build_payment_form_fields(*, order, amount):
    """Build the signed field set eSewa's v2 ePay form endpoint expects."""
    transaction_uuid = str(order.order_id)
    total_amount = f'{amount:.2f}'
    message = f'total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_MERCHANT_CODE}'

    return {
        'amount': total_amount,
        'tax_amount': '0',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': settings.ESEWA_MERCHANT_CODE,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': settings.ESEWA_SUCCESS_URL,
        'failure_url': settings.ESEWA_FAILURE_URL,
        'signed_field_names': SIGNED_FIELD_NAMES,
        'signature': _sign(message),
        'payment_url': settings.ESEWA_PAYMENT_URL,
    }


def decode_callback_payload(data_param: str) -> dict:
    decoded = base64.b64decode(data_param)
    return json.loads(decoded)


def verify_callback_signature(payload: dict) -> bool:
    signed_fields = payload.get('signed_field_names', '').split(',')
    message = ','.join(f'{field}={payload.get(field, "")}' for field in signed_fields)
    expected_signature = _sign(message)
    return hmac.compare_digest(expected_signature, payload.get('signature', ''))


def check_transaction_status(*, transaction_uuid: str, total_amount: str):
    """Call eSewa's status-check API as a server-side source of truth."""
    params = {
        'product_code': settings.ESEWA_MERCHANT_CODE,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
    }
    response = requests.get(settings.ESEWA_STATUS_CHECK_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
