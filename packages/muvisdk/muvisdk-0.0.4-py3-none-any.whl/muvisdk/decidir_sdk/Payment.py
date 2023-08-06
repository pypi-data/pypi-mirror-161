import requests
import json
from uuid import uuid4

from ..response import ok, error


class Payment:
    def __init__(self, url, private_key: str, public_key: str):
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, payment_data: dict, client: dict):
        body = {
            'customer': {
                'id': client['decidir_id'],
                'email': client['email']
            },
            'site_transaction_id': str(uuid4()),  # Debe ser unico? Unico por cliente o por merchant?
            # 'site_id': 28464385, # opcional
            'token': payment_data['token'],
            'payment_method_id': 1,    # Peso Argentino
            'bin': '450799',    # ?
            # se multiplica por 100; no acepta decimales.
            'amount': round(payment_data['transaction_amount'], 2) * 100,
            'currency': 'ARS',
            'installments': 1,
            'payment_type': 'single',
            'establishment_name': 'Cadena',  # opcional
            'sub_payments': []
        }
        r = requests.post(self.url + '/payments', headers=self.headers, data=json.dumps(body))
        if r.status_code < 400:
            return ok(r.json())
        return error(r.json())

    def get(self, payment_id: int):
        r = requests.get(self.url + '/payments/{}'.format(payment_id), headers=self.headers)
        return ok(r.json())
