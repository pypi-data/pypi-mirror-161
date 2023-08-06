import mercadopago

from ..response import ok, error


def _format(response):
    return {
        'id': response['id'],
        'card_type': response['payment_method']['payment_type_id'],
        'card_brand': response["payment_method"]["name"],
        'last_four_digits': response['last_four_digits'],
        'issuer': {
            'name': response['issuer']['name']
        },
        'cardholder': {
            'name': response['cardholder']['name']
        },
        'expiration_month': response['expiration_month'],
        'expiration_year': response['expiration_year'],
        'payer_id': response['user_id']
    }


class Card:
    def __init__(self, sdk: mercadopago.SDK):
        self.sdk = sdk

    def create(self, customer_id: str, card_token: str):
        card_data = {'token': card_token}
        mp_response = self.sdk.card().create(customer_id, card_data)

        if mp_response['status'] < 400:
            return ok(_format(mp_response['response']))

        return error(mp_response['response']['error'])
        
    def get(self, customer_id: str, card_id: str) -> dict:
        mp_response = self.sdk.card().get(customer_id, card_id)
        if mp_response['status'] < 400:
            card = mp_response['response']
            return ok(_format(card))

        return error(mp_response['response']['message'])

    def list_all(self, customer_id: str):
        cards = self.sdk.card().list_all(customer_id)
        if cards['status'] > 299:
            return error('Customer not found')
        else:
            cards = cards['response']
            return ok([_format(card) for card in cards])
