import mercadopago

from ..response import ok, error


class CardToken:
    def __init__(self, sdk: mercadopago.SDK):
        self.sdk = sdk

    def create(self, card_id: int):
        data = {"card_id": card_id}
        card_token_response = self.sdk.card_token().create(data)

        if card_token_response["status"] > 299:
            return error("Falló la creación de token de la tarjeta.",)

        return ok(card_token_response["response"]["id"])
