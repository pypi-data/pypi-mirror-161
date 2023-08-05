import time
import email
import zeep.exceptions
import dateutil.parser
import xmltodict
import xml.etree.ElementTree as ET
from pprint import pprint
from cryptography import x509
from cryptography.hazmat.bindings.openssl.binding import Binding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dateutil.relativedelta import *
from .dates import today_argentina, localize
from .format import muvi_print
from .init_creds import test,init_mongo
import datetime
import os

TIME_TO_EXPIRATION = 12  # In hours


def make_xml(service):
    timestamp = int(time.time())
    unique_id = f"<uniqueId>{timestamp}</uniqueId>"
    created_at = today_argentina().isoformat(timespec="seconds")
    created_at = f"<generationTime>{created_at}</generationTime>"
    expires_at = (today_argentina() + relativedelta(hours=TIME_TO_EXPIRATION)
                  ).isoformat(timespec="seconds")
    expires_at = f"<expirationTime>{expires_at}</expirationTime>"
    header = f"{unique_id}{created_at}{expires_at}"
    body = f"<header>{header}</header><service>{service}</service>"
    print('Generation_time', created_at)
    print('Expiration_time:', expires_at)
    return f'<?xml version="1.0" encoding="UTF­8"?><loginTicketRequest version="1.0">{body}</loginTicketRequest>'


def sign_xml(tra, cert, private_key):
    if isinstance(tra, str):
        tra = tra.encode('utf8')

    if Binding:
        _lib = Binding.lib
        _ffi = Binding.ffi

        bio_in = _lib.BIO_new_mem_buf(tra, len(tra))
        if not private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
            if isinstance(private_key, str):
                private_key = private_key.encode("utf-8")

        if isinstance(private_key, str):
            private_key = private_key.encode("utf-8")
        private_key = serialization.load_pem_private_key(
            private_key, None, default_backend()
        )

        if not cert.startswith("-----BEGIN CERTIFICATE-----"):
            if isinstance(cert, str):
                cert = cert.encode("utf-8")
        if isinstance(cert, str):
            cert = cert.encode("utf-8")
        cert = x509.load_pem_x509_certificate(cert, default_backend())

        try:
            # Firmar el texto (tra) usando cryptography (openssl bindings para python)
            p7 = _lib.PKCS7_sign(
                cert._x509, private_key._evp_pkey, _ffi.NULL, bio_in, 0
            )
        finally:
            # Liberar memoria asignada
            _lib.BIO_free(bio_in)
        # Se crea un buffer nuevo porque la firma lo consume
        bio_in = _lib.BIO_new_mem_buf(tra, len(tra))
        try:
            # Crear buffer de salida
            bio_out = _lib.BIO_new(_lib.BIO_s_mem())
            try:
                # Instanciar un SMIME
                _lib.SMIME_write_PKCS7(bio_out, p7, bio_in, 0)

                # Tomar datos para la salida
                result_buffer = _ffi.new("char**")
                buffer_length = _lib.BIO_get_mem_data(
                    bio_out, result_buffer)
                output = _ffi.buffer(result_buffer[0], buffer_length)[:]
            finally:
                _lib.BIO_free(bio_out)
        finally:
            _lib.BIO_free(bio_in)

        # Generar p7 en formato mail y recortar headers
        msg = email.message_from_string(output.decode("utf8"))
        for part in msg.walk():
            filename = part.get_filename()
            if filename == "smime.p7m":
                # Es la parte firmada?
                # Devolver CMS
                return part.get_payload(decode=False)


def analize_cert(crt, binary=False):
    "Carga un certificado digital y extrae los campos más importantes"

    if binary:
        cert = x509.load_pem_x509_certificate(crt, default_backend())
    else:
        if not crt.startswith("-----BEGIN CERTIFICATE-----"):
            crt = open(crt).read()
            if isinstance(crt, str):
                crt = crt.encode("utf-8")
        if isinstance(crt, str):
            crt = crt.encode("utf-8")
        cert = x509.load_pem_x509_certificate(crt, default_backend())
    certificate = dict()
    if cert:
        certificate = {
            'identidad': cert.subject,
            'caducidad': cert.not_valid_after,
            'emisor': cert.issuer,
            'certX509': cert
        }
    return certificate


def call_wsaa(client, cms, config, update_db=False):
    db = init_mongo()
    try:
        xml = client.service.loginCms(cms)
        xml = xml.replace('<?xml version="1.0" encoding="UTF8" standalone="yes"?>', '')
        xml = xml.replace('<?xml version="1.0" encoding="UTF8"?>', '')
        ticket = xmltodict.parse(xml)
        new_afip = {
            'token': ticket['loginTicketResponse']['credentials']['token'],
            'sign': ticket['loginTicketResponse']['credentials']['sign'],
            'expiration_token_date': dateutil.parser.parse(ticket['loginTicketResponse']['header']['expirationTime'])
        }
        if test:
            print('Guardando el backup...')
            now_str = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            try:
                os.mkdir('backup_token')
            except:
                pass
            f = open('backup_token/token_backup_' + now_str + '.json', "w")
            f.write(str(new_afip))
            f.close()
        if update_db:
            print('Guardando en la base de datos...')
            r = db.configuraciones.update_one({'_id': config['_id']}, {'$set': new_afip})
            muvi_print('succesful', f"Se actualizo {r.modified_count} config")
        else:
            muvi_print('warning', 'WARNING! Se opto por no realizar un update en la base de datos')
        return new_afip
    except zeep.exceptions.Fault as e:
        print(f'Error: {e.code}: {e.message}')
        return


def authorize(client, config, service) -> dict:
    ticket = dict()
    if 'expiration_token_date' in config.keys():
        if localize(config['expiration_token_date']) > today_argentina():
            print('Token no vencido, se busca en la DB...')
            ticket['token'] = config['token']
            ticket['sign'] = config['sign']
            ticket['expiration_token_date'] = config['expiration_token_date']
            muvi_print('successful', 'TOKEN OBTENIDO DE LA DB CON EXITO')
            return ticket
        else:
            tra = make_xml(service)
            cms = sign_xml(tra=tra, cert=config['certificado'], private_key=config['private_key'])
            ticket = call_wsaa(client, cms, config, True)
            if ticket:
                muvi_print('successful', 'TOKEN CREADO CON EXITO')
            else:
                muvi_print('error', 'ERROR AL CREAR EL TOKEN')
            return ticket
    else:
        tra = make_xml(service)
        cms = sign_xml(tra=tra, cert=config['certificado'], private_key=config['private_key'])
        ticket = call_wsaa(client, cms, config, True)
        if ticket:
            muvi_print('successful', 'TOKEN CREADO CON EXITO')
        else:
            muvi_print('error', 'ERROR AL CREAR EL TOKEN')
        return ticket
