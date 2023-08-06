import bson
from zeep import Client
from .init_creds import test, init_mongo
from .format import muvi_print
from .authorization import authorize

from pprint import pprint


class AFIP():
    config = None
    wsaa_client = None
    service_client = None
    ticket = None
    def __init__(self, config_id: bson.ObjectId) -> None:
        """ Método constructor

        :param config_id: id de la configuracion de afip
        :type config_id: bson.ObjectId
        """
        # * Buscar configuracion en db y obtener certificados
        db = init_mongo()
        self.config = db.configuraciones.find_one(config_id)
        #pprint(self.config)
        wsaa_testing = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL'
        wsaa_production = 'https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL'
        wsdl_testing = 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL'
        wsdl_production = 'https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL'

        try:
            self.wsaa_client = Client(
                wsaa_testing if test else wsaa_production)
            self.service_client = Client(
                wsdl_testing if test else wsdl_production)
        except Exception as e:
            print(e)
            self.wsaa_client = None
            self.service_client = None

    def make_token(self, service: str = 'wsfe') -> None:
        """ Método que genera un xml, lo firma y crea un token, si el merchant para el cual se quiere facturar
        ya tiene un token válido lo reutiliza, caso contrario genera uno nuevo

        :param service: servicio para el cual se quiere crear un token
        :type service: str
        :return: diccionario con datos del token
        :rtype: dict
        """
        ticket = authorize(self.wsaa_client, self.config, service)
        if ticket:
            self.ticket = ticket
        return

    def get_status(self):
        """
        Método dummy para comprobar estado del servidor
        """
        ret = self.service_client.service.FEDummy()
        return ret


    def consultarPuntosVenta(self,merchant:dict) -> list:
        """ Método que informa todos los puntos de venta habilitados para una cuit

        :return: lista de puntos de venta
        :rtype: list
        """
        ret = self.service_client.service.FEParamGetPtosVenta(
            Auth={
                'Token': self.ticket['token'],
                'Sign': self.ticket['sign'],
                'Cuit': merchant['afip']['cuit']
            },
        )
        return ret

    def autorizarComprobante(self, factura: dict,merchant:dict):
        try:
            ret = self.service_client.service.FECAESolicitar(
                Auth={
                    'Token': self.ticket['token'],
                    'Sign': self.ticket['sign'],
                    'Cuit': merchant['afip']['cuit']
                },
                FeCAEReq=factura
            )
            return ret

        except Exception as e:
            muvi_print('warning', '-- Cae no generado --')
            print('Socio: ', factura['FeDetReq']['FECAEDetRequest']['DocNro'])
            muvi_print('error', e)
            return

    def ultimoAutorizado(self, tipo_cbte: int, merchant:dict) -> dict:
        try:
            ret = self.service_client.service.FECompUltimoAutorizado(
                Auth={
                    'Token': self.ticket['token'],
                    'Sign': self.ticket['sign'],
                    'Cuit': merchant['afip']['cuit']
                },
                PtoVta=merchant['afip']['pto_venta'],
                CbteTipo=tipo_cbte
            )
            return ret
        except Exception as e:
            muvi_print('error', e)

    def recuperarComprobante(self, tipo_cbte: int, cbte_nro: int,merchant:dict) -> dict:
        ret = self.service_client.service.FECompConsultar(
            Auth={
                'Token': self.ticket['token'],
                'Sign': self.ticket['sign'],
                'Cuit': merchant['afip']['cuit']
            },
            FeCompConsReq={
                'CbteTipo': tipo_cbte,
                'CbteNro': cbte_nro,
                'PtoVta': merchant['afip']['pto_venta']
            }
        )
        return ret

    def consultarTiposDocumento(self,merchant:dict) -> list:
        """ Método que informa todos los posibles tipos de documentos a los que se les puede generar un comprobante

        :return: lista de tipos de documentos
        :rtype: list
        """
        ret = self.service_client.service.FEParamGetTiposDoc(
            Auth={
                'Token': self.ticket['token'],
                'Sign': self.ticket['sign'],
                'Cuit': merchant['afip']['cuit']
            }
        )
        return ret['ResultGet']['DocTipo']

    def consultarCondicionesIVA(self,merchant:dict) -> list:
        """ Método que informa todas las condiciones IVA disponibles

        :return: lista de condiciones IVA
        :rtype: list
        """
        ret = self.service_client.service.FEParamGetTiposIva(
            Auth={
                'Token': self.ticket['token'],
                'Sign': self.ticket['sign'],
                'Cuit': merchant['afip']['cuit']
            }
        )
        return ret['ResultGet']['IvaTipo']

    def consultarCotizacionMoneda(self, codigo_moneda: str,merchant:dict) -> dict:
        """ Método que informa la cotizacion para una moneda

        :param codigo_moneda: código de la moneda a consultar ('PES' para peso argentino) ver método consultarMonedas
        :type codigo_moneda: str
        :return: _description_
        :rtype: dict
        """
        ret = self.service_client.service.FEParamGetCotizacion(
            Auth={
                'Token': self.ticket['token'],
                'Sign': self.ticket['sign'],
                'Cuit': merchant['afip']['cuit']
            },
            MonId=codigo_moneda
        )
        return ret['ResultGet']

    def consultarMonedas(self,merchant:dict) -> list:
        """ Método que informa las distintas monedas disponibles

        :return: lista de monedas
        :rtype: list
        """
        ret = self.service_client.service.FEParamGetTiposMonedas(
            Auth={
                'Token': self.ticket['token'],
                'Sign': self.ticket['sign'],
                'Cuit': merchant['afip']['cuit']
            }
        )
        return ret['ResultGet']
