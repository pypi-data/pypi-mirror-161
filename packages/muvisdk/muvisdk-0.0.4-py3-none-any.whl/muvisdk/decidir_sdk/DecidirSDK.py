from .Customer import Customer
from .Card import Card
from .CardToken import CardToken
from .Payment import Payment


class DecidirSDK:
    def __init__(self, merchant):
        credentials = merchant['credentials']
        self.url = 'https://developers.decidir.com/api/v2'
        self.private_key = credentials['decidir']['access_token']
        self.public_key = credentials['decidir']['public_key']
        self.merchant_id = merchant['_id']
        self.merchant_name = merchant['name']

    def customer(self):
        return Customer(self.url, self.private_key, self.public_key)
    
    def card(self):
        return Card(self.url, self.private_key, self.public_key)

    def card_token(self):
        return CardToken(self.url, self.private_key, self.public_key)

    def payment(self):
        return Payment(self.url, self.private_key, self.public_key)
