# -*- coding: utf-8 -*-
"""
Module containing actions that modify the namespace of the XML elements.
"""

from lxml import etree
from glamconv.ead.utils import NS, split_qname
from glamconv.ead.formats import EAD_2002, EAD_APE
from glamconv.transformer.actions import TransformAction


class EadNamespaceAdder(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "ead-namespace-adder"
    name = "Adding the Ape-EAD namespace"
    category = "Naming"
    desc = (
        "This action puts all the XML elements with an empty namespace "
        "inside the Ape-EAD standard namespace. The attribute names are "
        "not changed. All the other actions designed for EAD-2002 "
        "documents expect the elements to have an empty namespace "
        "(such as the elements in EAD 2002). Therefore, be sure to run "
        "this action at the end of the transformation, just before the "
        "Ape-EAD validation."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        for elt in xml_root.iter(etree.Element):
            namespace, local_name = split_qname(elt.tag)
            if namespace is None:
                elt.tag = f"{{{NS['ead']}}}{local_name}"
                count += 1
        if count > 0:
            logger.info(
                f"{count:d} elements with an empty namespace have been "
                "transfered in Ape-EAD namespace"
            )
        return xml_root


class EadNamespaceRemover(TransformAction):
    applicable_for = (EAD_2002, EAD_APE)
    uid = "ead-namespace-remover"
    name = "Removing the Ape-EAD namespace"
    category = "Naming"
    desc = (
        "This action puts all the XML elements with the Ape-EAD standard "
        "namespace inside the empty namespace. The attribute names are "
        "not changed. This action does the opposite of the action that "
        "adds the Ape-EAD namespace to the XML elements."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        for elt in xml_root.iter(etree.Element):
            namespace, local_name = split_qname(elt.tag)
            if namespace == NS["ead"]:
                elt.tag = f"{{}}{local_name}"
                count += 1
        if count > 0:
            logger.info(
                f"{count:d} elements with the Ape-EAD namespace have been "
                "transfered in the empty namespace"
            )
        return xml_root
