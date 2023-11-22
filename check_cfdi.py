# -*- coding: utf-8 *-
import logging
import argparse
from lxml import etree
from collections import defaultdict

from errors import Errors



class CheckCFDI:

    def __init__(self, xml_path=None, loglevel='warning'):
        self.set_loglevel(loglevel)
        self.xml_etree = CheckCFDI.get_element_by_path(xml_path)
        self.namespaces_dict = self.xml_etree.nsmap
        self.incidents = defaultdict(list)

    def set_loglevel(self, loglevel):
        logging.basicConfig( level=loglevel.upper() )

    @staticmethod
    def get_element_by_path(xml_path):
        element_tree = etree.parse(xml_path)
        return element_tree.getroot()

    def validate(self):
        self.validate_concepts()

    def validate_concepts(self):
        conceptos = self.xml_etree.xpath('.//cfdi:Conceptos/cfdi:Concepto', namespaces=self.namespaces_dict)
        logging.debug(f'Procesando {len(conceptos)} conceptos.')
        for concepto in conceptos:
            no_identificacion = concepto.get("NoIdentificacion")
            impuestos = concepto.findall('.//cfdi:Impuestos', namespaces=self.namespaces_dict)
            traslados = concepto.xpath('.//cfdi:Impuestos/cfdi:Traslados/cfdi:Traslado', namespaces=self.namespaces_dict)
            retenciones = concepto.xpath('.//cfdi:Impuestos/cfdi:Retenciones/cfdi:Retencion', namespaces=self.namespaces_dict)
            if impuestos and not (traslados or retenciones):
                logging.debug(f'El concepto con NoIdentificación {no_identificacion}'\
                    f' presenta la incidencia: {Errors.CFDI40173}.')
                self.incidents[no_identificacion].append(
                    Errors.CFDI40173
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Valida/Corrige CFDI según las validaciones definidas')
    parser.add_argument('-x', '--xml_path', type=str, help='Ruta archivo CFDI', required=True)
    parser.add_argument( '-l',
                     '--loglevel',
                     default='warning',
                     help='Establece el nivel de log. ejemplo --loglevel debug, default=warning' )
    args = parser.parse_args()
    check_cfdi_obj = CheckCFDI(args.xml_path, args.loglevel)
    check_cfdi_obj.validate()