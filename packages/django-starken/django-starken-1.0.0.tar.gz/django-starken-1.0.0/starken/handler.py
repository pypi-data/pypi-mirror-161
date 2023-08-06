# -*- coding: utf-8 -*-
import logging
import datetime

from starken.connector import Connector, ConnectorException
from starken.settings import api_settings

logger = logging.getLogger(__name__)


class StarkenHandler:
    """
        Handler to connect with Starken
    """

    def __init__(self,  base_url=api_settings.STARKEN['BASE_URL'], verify=True):
        self.base_url = base_url
        self.verify = verify
        self.connector = Connector(verify_ssl=self.verify)

    def get_shipping_label(self):
        raise NotImplementedError(
            'get_shipping_label is not a method implemented for StarkenHandler')

    def get_default_payload(self, instance):
        """
            This method generates by default all the necessary data with
            an appropriate structure for Starken courier.
        """
        split_name = instance.customer.full_name.split()
        value_declared = 0
        for value in instance.items:
            value_declared += (int(value.price) * int(value.quantity))
        payload = {
            "rutEmpresaEmisora": api_settings.SENDER['RUT_COMPANY'],
            "rutUsuarioEmisor": api_settings.STARKEN['RUT_USER'],
            "claveUsuarioEmisor": api_settings.STARKEN['PASS_USER'],
            "rutDestinatario": instance.customer.rut,
            "dvRutDestinatario": "",
            "nombreRazonSocialDestinatario": split_name[0],
            "apellidoPaternoDestinatario": split_name[1],
            "apellidoMaternoDestinatario": '.' if len(split_name) <= 2 else split_name[2],
            "direccionDestinatario": instance.address.street,
            "numeracionDireccionDestinatario": instance.address.number,
            "departamentoDireccionDestinatario": instance.address.unit,
            "comunaDestino": instance.commune.name,
            "telefonoDestinatario": instance.customer.phone,
            "emailDestinatario": "",
            "nombreContactoDestinatario": instance.customer.full_name,
            "tipoEntrega": "2",
            "tipoPago": "2",
            "numeroCtaCte": api_settings.SENDER['CTA_CTE_NUMBER'],
            "dvNumeroCtaCte": api_settings.SENDER['DV_CTA_CTE_NUMBER'],
            "centroCostoCtaCte": api_settings.SENDER['CENTER_COST_CTA_CTE'],
            "valorDeclarado": value_declared,
            "contenido": instance.reference,
            "kilosTotal": "1",
            "alto": "1",
            "ancho": "1",
            "largo": "1",
            "tipoServicio": "0",
            "tipoDocumento1": api_settings.SENDER['DOCUMENT_TYPE'],
            "numeroDocumento1": api_settings.SENDER['DOCUMENT_NUMBER'],
            "generaEtiquetaDocumento1": api_settings.SENDER['GENERATE_LABEL_DOCUMENT_1'],
            "tipoDocumento2": "",
            "numeroDocumento2": "",
            "generaEtiquetaDocumento2": "",
            "tipoDocumento3": "",
            "numeroDocumento3": "",
            "generaEtiquetaDocumento3": "",
            "tipoDocumento4": "",
            "numeroDocumento4": "",
            "generaEtiquetaDocumento4": "",
            "tipoDocumento5": "",
            "numeroDocumento5": "",
            "generaEtiquetaDocumento5": "",
            "tipoEncargo1": api_settings.SENDER['TYPE_ORDER_1'],
            "cantidadEncargo1": len(instance.items),
            "tipoEncargo2": "",
            "cantidadEncargo2": "",
            "tipoEncargo3": "",
            "cantidadEncargo3": "",
            "tipoEncargo4": "",
            "cantidadEncargo4": "",
            "tipoEncargo5": "",
            "cantidadEncargo5": "",
            "ciudadOrigenNom": api_settings.SENDER['ORIGIN_CITY'],
            "observacion": "",
            "codAgenciaOrigen": "",
            "latitud": "",
            "longitud": "",
            "precisión": "",
            "calidad": "",
            "match": ""
        }
        logger.debug(payload)
        return payload

    def create_shipping(self, data):
        """
            This method generate a Starken shipping.
            If the get_default_payload method returns data, send it here,
            otherwise, generate your own payload.
        """

        url = f'{self.base_url}'
        logger.debug(data)

        try:
            response = self.connector.post(url, data)
            response.update({
                'tracking_number': response['nroOrdenFlete'],
            })
            return response

        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(error.message, error.description, error.code) from error

    def get_tracking(self, identifier):
        raise NotImplementedError(
            'get_tracking is not a method implemented for StarkenHandler')

    def get_events(self, raw_data):
        """
            This method obtain array events.
            structure:
            {
                "codigo":227569,
                "ubicacionActual":"326",
                "numeroOrdenFlete":959284399,
                "folio":724175058,
                "tipoDocumento":4,
                "estadoMicro":3,
                "estadoMacro":2,
                "nombreEstadoHomologado":"RECIBIDO EN STARKEN",
                "reIntentoWebhook":0,
                "codCiudadDestino":266,
                "tripulacion":null,
                "rutEmpresa":76499449,
                "maquina":null,
                "urlImagen":"",
                "ciudadDestino":"SANTIAGO",
                "estadoEnReparto":0,
                "encargosTotales":1,
                "fechaHoraEvento":1632754923322,
                "codigoEstadoHomologado":"RECIBIDO EN STARKEN",
                "descripcionEstado":"RECIBIDO EN STARKEN",
                "latitud":"0",
                "longitud":"0",
                "rutRecibe":0,
                "dvRecibe":null,
                "nombreRecibe":null,
                "tipoDevolucion":null,
                "codigoInternoEstado":2,
                "codigoAgenciaDestino":1053,
                "intePersonalizada":0,
                "inteBeetrack":0,"inteWebhook":1,
                "reIntentoPersonalizada":0,
                "reIntentoBeetrack":0,
                "saludAcusoPersonalizada":0,
                "saludAcusoBeetrack":0,
                "saludAcusoWebhook":0,
                "ctacteNumero":"41966"
            }
            return [{
                'city': 'Santiago',
                'state': 'RM',
                'description': 'Llego al almacén',
                'date': '12/12/2021'
            }]
        """
        date = datetime.datetime.now()
        return [{
                'city': '',
                'state': '',
                'description': raw_data.get('descripcionEstado'),
                'date': date.strftime('%d/%m/%Y')
            }]

    def get_status(self, raw_data):
        """
            This method returns the status of the order and "is_delivered".
            structure:
            {
                "codigo":227569,
                "ubicacionActual":"326",
                "numeroOrdenFlete":959284399,
                "folio":724175058,
                "tipoDocumento":4,
                "estadoMicro":3,
                "estadoMacro":2,
                "nombreEstadoHomologado":"RECIBIDO EN STARKEN",
                "reIntentoWebhook":0,
                "codCiudadDestino":266,
                "tripulacion":null,
                "rutEmpresa":76499449,
                "maquina":null,
                "urlImagen":"",
                "ciudadDestino":"SANTIAGO",
                "estadoEnReparto":0,
                "encargosTotales":1,
                "fechaHoraEvento":1632754923322,
                "codigoEstadoHomologado":"RECIBIDO EN STARKEN",
                "descripcionEstado":"RECIBIDO EN STARKEN",
                "latitud":"0",
                "longitud":"0",
                "rutRecibe":0,
                "dvRecibe":null,
                "nombreRecibe":null,
                "tipoDevolucion":null,
                "codigoInternoEstado":2,
                "codigoAgenciaDestino":1053,
                "intePersonalizada":0,
                "inteBeetrack":0,"inteWebhook":1,
                "reIntentoPersonalizada":0,
                "reIntentoBeetrack":0,
                "saludAcusoPersonalizada":0,
                "saludAcusoBeetrack":0,
                "saludAcusoWebhook":0,
                "ctacteNumero":"41966"
            }

            status : ['EN BODEGA CLIENTE', 'RECIBIDO EN STARKEN', 'EN TRANSITO A DESTINO', 'RECIBIDO EN AGENCIA DESTINO',
                       'EN REPARTO A DOMICILIO', 'ENTREGADO', 'NO ENTREGADO', 'PENDIENTE', 'CERRADO CON EXCEPCION',
                       'REDESTINADO', 'ANULADO']
            response: ('ENTREGADO', True)
        """

        status = raw_data.get('nombreEstadoHomologado')
        is_delivered = False

        if status == 'ENTREGADO':
            is_delivered = True

        return status, is_delivered
