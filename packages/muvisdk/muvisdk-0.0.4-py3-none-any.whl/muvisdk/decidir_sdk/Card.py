import requests

from ..response import ok

card_brand = {
    1: 'Visa',
    8: 'Diners Club',
    23: 'Tarjeta Shopping',
    24: 'Tarjeta Naranja',
    25: 'PagoFacil',
    26: 'RapiPago',
    29: 'Italcred',
    30: 'ArgenCard',
    34: 'CoopePlus',
    37: 'Nexo',
    38: 'Credimás',
    39: 'Tarjeta Nevada',
    42: 'Nativa',
    43: 'Tarjeta Cencosud',
    44: 'Tarjeta Carrefour / Cetelem',
    45: 'Tarjeta PymeNacion',
    48: 'Caja de Pagos',
    50: 'BBPS',
    51: 'Cobro Express',
    52: 'Qida',
    54: 'Grupar',
    55: 'Patagonia 365',
    56: 'Tarjeta Club Día',
    59: 'Tuya',
    60: 'Distribution',
    61: 'Tarjeta La Anónima',
    62: 'CrediGuia',
    63: 'Cabal Prisma',
    64: 'Tarjeta SOL',
    65: 'American Express',
    103: 'Favacard',
    104: 'MasterCard Prisma',
    109: 'Nativa Prisma',
    111: 'American Express Prisma',

    # Debito
    31: 'Visa Débito',
    105: 'MasterCard Debit Prisma',
    106: 'Maestro Prisma',
    108: 'Cabal Débito Prisma'
}


def _card_type(payment_method_id):
    if payment_method_id in [31, 105, 106, 108]:
        return 'credit_card'
    return 'debit_card'


def _format(response, customer_id):
    return {
        'id': response['token'],
        'card_type': _card_type(response['payment_method_id']),
        'card_brand': card_brand[response['payment_method_id']],
        'last_four_digits': response['last_four_digits'],
        'issuer': {
            'name': card_brand[response['payment_method_id']]
        },
        'cardholder': {
            'name': response['card_holder']['name']
        },
        'expiration_month': response['expiration_month'],
        'expiration_year': response['expiration_year'],
        'payer_id': customer_id
    }


class Card:
    def __init__(self, url: str, private_key: str, public_key: str):
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, customer_id: str, card_token: str):
        """ Tokenizar la tarjeta

        :param customer_id: Id del cliente
        :type customer_id: str
        :param card_token: Token de la tarjeta
        :type card_token: str
        :return: Tarjeta con su token
        :rtype: dict
        """
        response = {
                'id': card_token
            }
        return ok(response)

    def get(self, customer_id: str, card_id: str):
        r = requests.get('{}/usersite/{}/cardtokens'.format(self.url, customer_id), headers=self.headers)
        cards = r.json()['tokens']

        for card in cards:
            if card['token'] == card_id:
                return ok(_format(card, customer_id))

    def list_all(self, customer_id: str):
        r = requests.get('{}/usersite/{}/cardtokens'.format(self.url, customer_id), headers=self.headers)
        cards = r.json()['tokens']
        return ok([_format(card, customer_id) for card in cards])
