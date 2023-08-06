import requests
import json

from ..response import ok, error


def _format(response):
    return {
        'email': response['email'],
        'first_name': response['nombre'],
        'last_name': response['apellido'],
    }


def check(client: dict) -> dict:
    lista = {
        'nombre': None,
        'apellido': None,
        'celular': None,
        'email': None
    }
    for k in lista.keys():
        if k not in client:
            client[k] = lista[k]
    if 'domicilio' not in client:
        client['domicilio'] = {
            'altura': '1',
            'calle': '-'
        }
    else:
        if 'calle' not in client['domicilio']:
            client['domicilio']['calle'] = '-'
        if 'altura' not in client['domicilio']:
            client['domicilio']['altura'] = '1'

    return client


class Customer:
    def __init__(self, url: str, private_key: str, public_key: str):
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, client: dict) -> dict:
        client = check(client)
        formatted_client = _format(client)
        customer = {
            'customer': {
                'name': '{} {}'.format(client['nombre'], client['apellido']),
                'identification': {
                    'type': 'dni',
                    'number': client['documento']
                }
            }
        }
        self.headers['apikey'] = self.public_key
        r = requests.post(self.url + '/tokens', headers=self.headers, data=json.dumps(customer))
        self.headers['apikey'] = self.private_key
        print(r.json())
        formatted_client['id'] = r.json()['id']

        return ok(formatted_client)

    def get(self, customer_id: str) -> dict:
        # No existen los datos del customer almacenados en decidir
        return error('Customer not found')

    def search(self, filters: dict):
        return error('Customer not found')