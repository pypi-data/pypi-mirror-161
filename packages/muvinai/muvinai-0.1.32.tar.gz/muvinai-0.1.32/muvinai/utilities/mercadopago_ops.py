import bson

from .init_creds import init_mongo, test

import mercadopago
import requests

db = init_mongo()


def get_payment(payment_id, sdk: mercadopago.sdk):
    response = sdk.payment().search(filters={"id": payment_id})
    return response["response"]


def get_merchant_from_payment(payment_id: str):
    """ Obtener el merchant a partir de un pago de mercadopago

          :param payment_id: id del pago
          :type payment_id: str
          :return: el merchant del pago
          :rtype: ObjectId
          """
    for merchant in db.merchants.find({"keys.access_token": {"$exists": True}}):
        try:
            sdk = mercadopago.SDK(merchant["keys"]["access_token"])
        except KeyError:
            continue
        payment = get_payment(payment_id, sdk)
        if "results" in payment.keys():
            if payment["results"]:
                return merchant["_id"]


def get_sdk_from_payment(payment_id: str):
    """ Obtener el sdk a partir de un pago de mercadopago

      :param payment_id: id del pago
      :type payment_id: str
      :return: el sdk ya instanciado de mercadopago
      :rtype: mercadopago.SDK
      """
    for merchant in db.merchants.find({"keys.access_token": {"$exists": True}}):
        try:
            sdk = mercadopago.SDK(merchant["keys"]["access_token"])
        except KeyError:
            continue
        payment = get_payment(payment_id, sdk)
        if "results" in payment.keys():
            if payment["results"]:
                return sdk


def get_payments_from_user_id(mp_id: str, sdk: mercadopago.sdk, days=30, limit=10):
    """ Obtener todos los pagos en los últimos <days> días para un usuario dado un mercadopago_id

          :param mp_id: id del usuario en mercadopago. Sólo los números antes de guión
          :type payment_id: str
          :param sdk: El SDK de mercadopago correspondiente al plan del usuario
          :type sdk: SDK.mercadopago
          :param mp_id: id del usuario en mercadopago. Sólo los números antes de guión
          :type days: int
          :param limit: límite de resultados a obtener
          :type limit: int
          :return: lista de pagos que satisfacen query
          :rtype: list
    """

    if "-" in mp_id:
        mp_id, x = mp_id.split("-")

    payment_info = {"begin_date": f"NOW-{days}DAYS",
                 "end_date": "NOW",
                 "range": "date_created",
                 "sort": "date_created",
                 "limit": limit,
                 "offset": 0,
                 "payer.id": mp_id
                 }

    payments = sdk.payment().search(filters=payment_info)

    return payments["response"]["results"]


def get_sdk_from_user(user_id: bson.ObjectId):
    """ Obtener el SDK de mercadopago a partir de un id de usuario

           :param user_id: id del usuario en mongoDB.
           :type payment_id: bson.ObjectId
           :return: sdk de mercadopago
           :rtype: mercadopago.SDK
           """
    client = db.clientes.find_one({"_id": user_id})
    plan = db.planes.find_one({"_id": client["active_plan_id"]})
    merchant = db.merchants.find_one({"_id": plan["merchant_id"]})
    sdk = mercadopago.SDK(merchant["keys"]["access_token"])
    return sdk


def get_sdk_from_merchant(merchant_id):
    merchant = db.merchants.find_one(bson.ObjectId(merchant_id))
    return mercadopago.SDK(merchant["keys"]["access_token"])


def mercadopago_client(sdk: mercadopago.SDK, cli: dict) -> str:
    """Método que crea un cliente en mercadopago o retorna el id si ya existe

    :param sdk: SDK de mercadopago ya instanciado
    :type sdk: mercadopago.SDK
    :param cli: datos del cliente a crear/buscar
    :type cli: dict
    :return: id del socio en mercadopago
    :rtype: str
    """

    customers_response = sdk.customer().search(filters={'email': cli['email']})
    customers = customers_response['response']

    try:
        street_number = int(cli['domicilio']['altura'])
    except:
        street_number = 1

    mp_customer_data = {
        "email": cli["email"],
        "first_name": cli["nombre"],
        "last_name": cli['apellido'],
        "phone": {"area_code": None, "number": cli['celular']},
        'identification': {'type': 'DNI', 'number': cli['documento']},  # ! Tipo de identificacion hardcodeado
        'address': {
            'street_name': cli['domicilio']['calle'],
            'street_number': street_number,
        }
    }
    if len(customers['results']) > 0:
        print("Cliente ya existente en Mercadopago...")
        print("Email: ", customers['results'][0]['email'])
        print("Mercadopago_id: ", customers['results'][0]['id'])
        # * Cliente ya existente
        customer = customers['results'][0]
    else:
        # * Creación de un cliente
        created_customer = sdk.customer().create(mp_customer_data)
        customer = created_customer['response']
        if 'email' in customer.keys():
            print("Cliente creado en Mercadopago")
            print("Email: ", customer['email'])
            print("Mercadopago_id: ", customer['id'])
        else:
            print('Fallo la creación del cliente en mp')
            print('Cliente con email: ', cli['email'])
            print(customer)
            customer['id'] = 'error'
    return customer['id']


def create_access_token(merchant: dict, marketplace: dict) -> dict:
    """ Método que crea un access token para el marketplace enviado por parámetro

    :param merchant: merchant para el cual se quieren crear credenciales.
    :type merchant: dict
    :param marketplace: marketplace a integrar, con formato de merchant.
    :type marketplace: dict
    :return: diccionario de keys.
    :rtype: dict
    """
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {merchant["keys"]["access_token"]}'
    }
    
    data = {
        'client_id': marketplace['keys_marketplace']['client_id'],
        'client_secret': marketplace['keys_marketplace']['client_secret'],
        'grant_type': 'authorization_code',
        'code': merchant['keys_marketplace']['marketplace_code'],
        'redirect_uri': 'http://localhost:3000/#/merchants' if test else 'https://www.app.apisportclub.xyz/#/merchants',
    }
    
    response = requests.post('https://api.mercadopago.com/oauth/token', json=data, headers=headers)
    response = response.json()
    
    keys = None
    if 'access_token' in response.keys():
        keys = {
            'access_token': response['access_token'],
            'refresh_token': response['refresh_token'],
            'public_key': response['public_key']
        }
    return keys


def refresh_token(merchant: dict, marketplace: dict) -> dict:
    """ Método que crea un access token para el marketplace enviado por parámetro

    :param merchant: merchant para el cual se quieren crear credenciales.
    :type merchant: dict
    :param marketplace: marketplace a integrar, con formato de merchant.
    :type marketplace: dict
    :return: diccionario de keys.
    :rtype: dict
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {merchant["keys"]["access_token"]}',
    }
    
    data = {
        "client_id": marketplace['keys_marketplace']['client_id'],   
        "client_secret": marketplace['keys_marketplace']['client_secret'],
        "grant_type": "refresh_token",
        "refresh_token": merchant["keys_marketplace"]["refresh_token"],
    }
    
    response = requests.post('https://api.mercadopago.com/oauth/token', json=data, headers=headers)
    response = response.json()
    
    keys = None
    if 'access_token' in response.keys():
        keys = {
            'access_token': response['access_token'],
            'refresh_token': response['refresh_token'],
            'public_key': response['public_key']
        }
    return keys


def get_mercadopago_client(sdk, mongo_client):
    customers_response = sdk.customer().search(filters={'id': mongo_client['mercadopago_id']})
    return customers_response['response']