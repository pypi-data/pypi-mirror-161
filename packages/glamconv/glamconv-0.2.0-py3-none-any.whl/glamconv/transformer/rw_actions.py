# -*- coding: utf-8 -*-
"""
Module defining basic read / write actions
"""

from lxml import etree

from glamconv.transformer.actions import ReadAction, WriteAction
from glamconv.ead.utils import NS


class XmlReader(ReadAction):
    uid = "xml-reader"
    name = "Reading of an XML file"
    desc = "This action reads an XML file and returns the XML data it contains."

    def _execute(self, input_flow, logger, log_details):
        if isinstance(input_flow, etree._Element):
            return input_flow
        if isinstance(input_flow, etree._ElementTree):
            return input_flow.getroot()
        tree = etree.parse(input_flow)
        xml_root = tree.getroot()
        return xml_root


class XmlWriter(WriteAction):
    uid = "xml-writer"
    name = "Writing an XML file"
    desc = "This action writes the XML data it receives into an XML file."

    def _execute(self, xml_root, logger, log_details):
        # beautify namespaces in output: use ead ns as the default one
        nsmap = NS.copy()
        nsmap[None] = nsmap.pop("ead")
        new_root = etree.Element("ead", nsmap=nsmap)
        new_root[:] = xml_root[:]
        new_root.text = xml_root.text
        new_root.tail = xml_root.tail
        return etree.tostring(
            new_root, encoding="UTF-8", xml_declaration=True, pretty_print=True
        )
