# -*- coding: utf-8 -*-

from os import path as osp
from lxml import etree
from glamconv.transformer.actions import ValidateAction


DTD_DIR = osp.join(osp.abspath(osp.dirname(__file__)), "ead-2002-dtd")
EAD_DTD = etree.DTD(osp.join(DTD_DIR, "ead.dtd"))

SCHEMA_DIR = osp.join(osp.abspath(osp.dirname(__file__)), "ape-ead-schema")
EAD_SCHEMA_XML = etree.parse(osp.join(SCHEMA_DIR, "apeEAD.xsd"))
EAD_SCHEMA = etree.XMLSchema(EAD_SCHEMA_XML)


class Ead2002Validator(ValidateAction):
    uid = "ead-2002-validator"
    name = "Validating XML data in EAD-2002 format"
    desc = "This action validates XML data against the EAD-2002 DTD."

    def _execute(self, xml_root, logger, log_details):
        result = EAD_DTD.validate(xml_root)
        if result is False:
            error_list = [
                f"Line {err.line}: {err.message}" for err in EAD_DTD.error_log
            ]
            err_num = len(error_list)
            if err_num > 100:
                error_list = error_list[:100]
                error_list.append(f"... and {(err_num - 100):d} more errors! ...")
            logger.error(
                "The XML data doesn't comply with the constraints defined in "
                "the EAD-2002 standard (DTD). The following validation "
                "errors have been found:",
                "\n".join(error_list),
            )
        else:
            logger.info("The XML data complies with the EAD-2002 standard (DTD).")
        return result


class ApeEadValidator(ValidateAction):
    uid = "ape-ead-validator"
    name = "Validating XML data in Ape-EAD format"
    desc = "This action validates XML data against the Ape-EAD XML Schema."

    def _execute(self, xml_root, logger, log_details):
        result = EAD_SCHEMA.validate(xml_root)
        if result is False:
            error_list = [
                f"Line {err.line}: {err.message}" for err in EAD_SCHEMA.error_log
            ]
            err_num = len(error_list)
            if err_num > 100:
                error_list = error_list[:100]
                error_list.append(f"... and {(err_num - 100):d} more errors! ...")
            logger.error(
                "The XML data doesn't comply with the constraints defined in "
                "the Ape-EAD standard (XML Schema). The following validation "
                "errors have been found:",
                "\n".join(error_list),
            )
        else:
            logger.info("The XML data complies with the Ape-EAD standard (XML Schema).")
        return result
