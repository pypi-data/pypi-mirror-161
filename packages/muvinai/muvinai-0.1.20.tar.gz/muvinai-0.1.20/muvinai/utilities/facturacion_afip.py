from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm,inch
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfFileWriter, PdfFileReader
import base64
import json
import qrcode
import locale
import io

def generateKey(cuit:str,bits:int=2048,save_file=False):
    """ Funcion para generar una private key con python

    :param cuit: CUIT a generar la PK
    :type cuit: int
    :param bits: Bits de la clave privada (2048 por default)
    :type bits: int
    :param type_pk: tipo de clave, por default TYPE_RSA
    :type type_pk: crypto Type
    :param save_file: si se desea guardar la clave en un archivo, False por default
    :type save_file: boolean
    :return: key
    :rtype: Key de PyOpenSSL

    """

    pk = rsa.generate_private_key(public_exponent=65537, key_size=bits, backend=default_backend)
    
    if save_file:
        keyfile = 'pk_' + cuit + '.key'
        f = open(keyfile, "wb")
        pk_byte = pk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        f.write(pk_byte)
        f.close()

    return pk

def generateCSR(cuit:str,razon_social:str,key,save_file=False):
    """ Funcion para generar el CSR

    :param cuit: CUIT a generar la PK
    :type cuit: int
    :param razon_social: Razon social del facturante
    :type razon_social: str
    :param save_file: si se desea guardar el certificado en un archivo, False por default
    :type save_file: boolean
    :return: CSR
    :rtype: string

    """
    
    CSR = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "muvi_facturacion"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "AR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, razon_social),
        x509.NameAttribute(NameOID.SERIAL_NUMBER, "CUIT" + cuit)
    ])).sign(key, hashes.SHA256())
    
    if save_file:
        csrfile = f'cert_{str(cuit)}.csr'
        f = open(csrfile, "wb")
        f.write(CSR.public_bytes(serialization.Encoding.PEM))
        f.close()
    return CSR


#### PDF PARA LAS FACTURAS

def format_numero_factura(pto_venta:int,cbte_num:int,tipo_cbte:int,short=False) -> str:
    if short:
        return "%03d" % (tipo_cbte,) + '_' + "%05d" % (pto_venta,) + '_' + "%08d" % (cbte_num,)

    if tipo_cbte == 6:
        nro_factura = 'Factura B - N°' + "%05d" % (pto_venta,) + '-' + "%08d" % (cbte_num,)
    elif tipo_cbte == 8:
        nro_factura = 'Nota de Crédito B - N°' + "%05d" % (pto_venta,) + '-' + "%08d" % (cbte_num,)
    else:
        nro_factura = 'Factura B - N°' + "%05d" % (pto_venta,) + '-' + "%08d" % (cbte_num,)
    return nro_factura

def limit_string(string:str,limit:int) -> str:

    if len(string) > limit:
        return string[:limit]
    else:
        return string

def make_qr(factura:dict, qr_path:str):

    url = "https://www.afip.gob.ar/fe/qr/?p=%s"

    data = {
        'ver': 1,
        'fecha': factura['data_factura']['fecha_factura'].strftime("%Y%m%d"),
        'cuit': int(factura['data_facturante']['cuit']),
        'ptoVta': int(factura['data_factura']['pto_venta']),
        'tipoCmp': int(factura['data_factura']['tipo_comprobante']),
        'nroCmp': int(factura['data_factura']['num_comprobante']),
        'importe': float(factura['data_venta']['importe_total']),
        'moneda': 'PES',
        'ctz': float(1.000),
        'tipoDocRec': 96, # Por que es DNI
        'nroDocRec': str(factura['data_cliente']['documento']),
        'tipoCodAut': 'E',  # CAE o A si CAEA
        'codAut': int(factura['data_cae']['cae'])
    }

    data_json = json.dumps(data)
    url = url % (base64.b64encode(data_json.encode('ascii')).decode('ascii'))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    img.save(qr_path, "PNG")
    print(f"QR creado en {qr_path}")

def make_factura_pdf(files_names:dict,factura:dict) -> list:
    """
    :param files_names: Nombres de los archivos,
    FILES_NAMES = {
        'QR_PATH':'...',
        'TEMPLATE_FACTURA':'...',
        'TEMPLATE_NOTA_DE_CREDITO':'...',
        'PDF_NAME':'...'}
    :param factura: Dict de factura proveniente de mongo
    :return: Lista con los archivos que genero
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    x_page = 210
    y_page = 297
    can.setPageSize(A4)

    #### FORMAT DEL PRECIO ################################
    locale.setlocale(locale.LC_ALL, 'es_AR')
    price = (locale.currency(factura['data_venta']['importe_total'], grouping=True))

    #### TIPO DE BOLETA ###################################
    can.setFillColorRGB(0.25, 0.25, 0.25)
    can.setFont("Helvetica-Bold", 42)
    can.drawString(99.5 * mm, (y_page - 45) * mm, "B")
    can.setFont("Helvetica-Bold", 12)
    can.drawString(96.5 * mm, (y_page - 52) * mm, "COD. 0"+str(factura['data_factura']['tipo_comprobante']))

    #### DATOS DEL FACTURANTE #############################
    can.setFillColorRGB(1, 1, 1)
    can.setFont("Helvetica-Bold", 11)
    can.drawString(126 * mm, (y_page - 35.2) * mm, format_numero_factura(int(factura['data_factura']['pto_venta']),int(factura['data_factura']['num_comprobante']),int(factura['data_factura']['tipo_comprobante'])))

    can.setFillColorRGB(0, 0, 0)
    can.setFont("Helvetica", 10)
    can.drawString(126 * mm, (y_page - 41.5) * mm, 'Fecha: ' + factura['data_factura']['fecha_factura'].strftime("%Y-%m-%d"))
    cuit = factura['data_facturante']['cuit']
    can.drawString(126 * mm, (y_page - 47) * mm, 'CUIT: '+cuit[0:2]+'-'+cuit[2:-1]+'-'+cuit[-1])
    can.drawString(126 * mm, (y_page - 52.5) * mm, 'Razon Social: ' + limit_string(factura['data_facturante']['razon_social'],40))
    can.drawString(126 * mm, (y_page - 58) * mm, 'Inicio de Actividades: '+factura['data_facturante']['inicio_de_actividades'].strftime("%Y-%m-%d"))
    can.drawString(126 * mm, (y_page - 63.5) * mm, 'Ingresos Brutos: '+ factura['data_facturante']['ii_bb'])

    can.setFillColorRGB(0.2, 0.2, 0.2)
    can.setFont("Helvetica-Bold", 11)
    can.drawString(8 * mm, (y_page - 36) * mm, 'DATOS DEL FACTURANTE')
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Helvetica", 10)
    direccion_facturante = limit_string(factura['data_facturante']['domicilio']['calle'],45) + ' ' + factura['data_facturante']['domicilio']['altura']
    can.drawString(8 * mm, (y_page - 41.5) * mm, 'Dirección: '+direccion_facturante)
    can.drawString(8 * mm, (y_page - 47) * mm, limit_string(factura['data_facturante']['domicilio']['localidad'],50))
    can.drawString(8 * mm, (y_page - 52.5) * mm, 'Teléfono: ' + factura['data_facturante']['telefono'])
    can.drawString(8 * mm, (y_page - 58) * mm, 'Email: ' + factura['data_facturante']['email'])
    can.drawString(8 * mm, (y_page - 63.5) * mm, 'IVA RESPONSABLE INSCRIPTO')

    #### DATOS DE LAS CONDICIONES DE VENTA ################
    can.setFillColorRGB(0.2, 0.2, 0.2)
    can.setFont("Helvetica-Bold", 10)
    can.drawString(120 * mm, (y_page - 74) * mm, 'CONDICIONES DE VENTA')
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Helvetica", 9)
    if 'payment_type' in factura['data_factura']:
        if 'payment_type' == '':
            metodo_de_pago = 'MercadoPago'
        elif 'payment_type' == 'cash':
            metodo_de_pago = 'Efectivo'
        else:
            metodo_de_pago = '-'
    else:
        metodo_de_pago = '-'
    can.drawString(120 * mm, (y_page - 82) * mm, 'Método de pago:' + metodo_de_pago)
    can.drawString(120 * mm, (y_page - 88) * mm, 'Tipo: Servicios')
    can.drawString(120 * mm, (y_page - 94) * mm, 'Fecha de inicio de servicios: ' + factura['data_venta']['inicio_servicios'].strftime("%Y-%m-%d"))
    can.drawString(120 * mm, (y_page - 100) * mm, 'Fecha de fin de servicios: ' + factura['data_venta']['fin_servicios'].strftime("%Y-%m-%d"))
    can.drawString(120 * mm, (y_page - 106) * mm, 'Fecha de pago del servicio: ' + factura['data_venta']['fecha_pago'].strftime("%Y-%m-%d"))

    #### DATOS DEL CLIENTE ################################
    can.setFillColorRGB(0.2, 0.2, 0.2)
    can.setFont("Helvetica-Bold", 10)
    can.drawString(8 * mm, (y_page - 74) * mm, 'INFORMACIÓN DEL CLIENTE')
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Helvetica", 10)
    cliente_name = limit_string(factura['data_cliente']['nombre'],30) + " " + factura['data_cliente']['apellido']
    can.drawString(8 * mm, (y_page - 80) * mm, 'Cliente: '+limit_string(cliente_name,55))
    direccion_cliente = limit_string(factura['data_cliente']['domicilio']['calle'],45) + ' ' + factura['data_cliente']['domicilio']['altura']
    can.drawString(8 * mm, (y_page - 86) * mm, 'Direccion: '+ limit_string(direccion_cliente,55))
    can.drawString(8 * mm, (y_page - 92) * mm, 'Provincia: ' + factura['data_cliente']['domicilio']['provincia'])
    can.drawString(8 * mm, (y_page - 98) * mm, 'Email: '+factura['data_cliente']['email'])
    can.drawString(8 * mm, (y_page - 104) * mm, 'Documento:'+str(factura['data_cliente']['documento']))
    can.drawString(8 * mm, (y_page - 110) * mm, 'Condición: Consumidor Final')

    #### CONCEPTOS ########################################
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Helvetica", 10)
    # Cantidad
    can.drawString(10 * mm, (y_page - 128.5) * mm, "1,00")
    # Descripcion del Plan
    can.drawString(42 * mm, (y_page - 128.5) * mm, factura['data_plan']['plan_name'])
    # Subtotal
    can.drawString(150 * mm, (y_page - 128.5) * mm,price)
    # Total
    can.drawString(178 * mm, (y_page - 128.5) * mm,price)
    # Si se desea agregar otro item deberia ser en la altura 138.5

    #### PRICES ###########################################
    can.setFillColorRGB(0,0,0)
    can.setFont("Helvetica",11)
    can.drawString(120 * mm, (y_page - 226) * mm, "Subtotal")
    can.drawString(165 * mm, (y_page - 226) * mm, price)
    can.drawString(120 * mm, (y_page - 240) * mm, "Total Descuento")
    can.drawString(165 * mm, (y_page - 240) * mm, price)
    can.setFillColorRGB(1,1,1)
    can.setFont("Helvetica-Bold",15)
    can.drawString(120 * mm, (y_page-252) * mm, "Final Total")
    can.drawString(165 * mm, (y_page-252) * mm, price)

    #### CAE y QR #########################################
    result_qr = make_qr(factura,files_names['QR_PATH'])
    print(result_qr)
    can.setFillColorRGB(0.1, 0.1, 0.1)
    can.setFont("Helvetica-Bold", 11)
    can.drawString(46 * mm, (y_page-268) * mm, 'N° de CAE: ' + factura['data_cae']['cae'])
    can.drawString(46 * mm, (y_page-278) * mm, 'Fecha de Vencimiento: ' + factura['data_cae']['fecha_vencimiento'].strftime('%d/%m/%Y'))
    can.drawInlineImage(files_names['QR_PATH'], x=15*mm, y=(y_page-284.5)*mm, width=26 * mm, height=26 * mm)

    #### NOTA DE CREDITO ##################################
    if 'data_nota_de_credito' in factura:
        can.setFillColorRGB(0, 0, 0)
        can.setFont("Helvetica", 10)
        can.drawString(8 * mm, (y_page - 226) * mm, 'Nota de crédito B, asociada con:')
        can.drawString(8 * mm, (y_page - 232) * mm, format_numero_factura(pto_venta=factura['data_nota_de_credito']['factura_asociada']['pto_venta'],
                                                                          cbte_num=factura['data_nota_de_credito']['factura_asociada']['num_comprobante'],
                                                                          tipo_cbte=factura['data_nota_de_credito']['factura_asociada']['tipo_comprobante']))

    #### SE GUARDA EL PDF #################################
    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    if factura['data_factura']['tipo_comprobante'] == 6:
        existing_pdf = PdfFileReader(open(files_names['TEMPLATE_FACTURA'], "rb"))
    elif factura['data_factura']['tipo_comprobante'] == 8:
        existing_pdf = PdfFileReader(open(files_names['TEMPLATE_NOTA_DE_CREDITO'], "rb"))
    output = PdfFileWriter()
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    outputStream = open(files_names['PDF_NAME'], "wb")
    output.write(outputStream)
    outputStream.close()
    return files_names['PDF_NAME']

def make_name_pdf(factura:dict) -> str:
    name_pdf = str(factura['data_facturante']['cuit'])+'_'+format_numero_factura(int(factura['data_factura']['pto_venta']),
                                                                                 int(factura['data_factura']['num_comprobante']),
                                                                                 int(factura['data_factura']['tipo_comprobante']),
                                                                                 short=True)+'.pdf'
    return name_pdf


