import mercadopago
from iso8601 import parse_date

from ..response import ok, error


def _format_card(response):
    return {
        'id': response['id'],
        'card_type': response['payment_type_id'],
        'last_four_digits': response['card']['last_four_digits'],
        'cardholder': {
            'name': response['card']['cardholder']['name']
        },
        'expiration_month': response['card']['expiration_month'],
        'expiration_year': response['card']['expiration_year'],
    }


def _format(response):
    return {
        'id': response['id'],
        'transaction_amount': response['transaction_amount'],
        'date_created': parse_date(response['date_created']),
        'status': response['status'],
        'status_detail': response['status_detail'],
        'card': _format_card(response)
    }


class Payment:
    def __init__(self, sdk: mercadopago.SDK):
        self.sdk = sdk

    def create(self, payment_data: dict):
        payment_data_mp = {
            "notification_url": None,
            "transaction_amount": round(payment_data['transaction_amount'], 2),
            "token": payment_data['token'],
            "installments": 1,
        }

        if 'additional_info' in payment_data:
            payment_data_mp["additional_info"] = payment_data['additional_info']
        if 'description' in payment_data:
            payment_data_mp["description"] = payment_data['description']
        if 'payer' in payment_data:
            payment_data_mp["payer"] = payment_data['payer']
        if 'external_reference' in payment_data:
            payment_data_mp["external_reference"] = payment_data['external_reference']
        if 'point_of_interaction' in payment_data:
            payment_data_mp["point_of_interaction"] = payment_data['point_of_interaction']
        if 'installments' in payment_data:
            payment_data_mp["installments"] = payment_data['installments']

        payment_response = self.sdk.payment().create(payment_data_mp)
        if payment_response['status'] < 400:
            return ok(_format(payment_response['response']))

        return error(payment_response['response']['message'])

    def get(self, payment_id: int):
        payment_response = self.sdk.payment().get(payment_id)
        if payment_response['status'] < 400:
            return ok(payment_response['response'])

        return error(payment_response['response']['message'])
