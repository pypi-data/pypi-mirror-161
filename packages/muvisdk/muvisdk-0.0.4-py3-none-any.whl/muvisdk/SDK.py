from .mercadopago_sdk.MercadoPagoSDK import MercadoPagoSDK
from .decidir_sdk.DecidirSDK import DecidirSDK


class SDK:
    def __init__(self, merchant):
        if 'credentials' in merchant and merchant['credentials']['preferred_processor'] == 'decidir':
            self._sdk = DecidirSDK(merchant)
        else:
            self._sdk = MercadoPagoSDK(merchant)

    def customer(self):
        return self._sdk.customer()

    def card(self):
        return self._sdk.card()

    def card_token(self):
        return self._sdk.card_token()

    def payment(self):
        return self._sdk.payment()
