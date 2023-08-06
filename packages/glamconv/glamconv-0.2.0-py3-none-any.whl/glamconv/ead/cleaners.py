# -*- coding: utf-8 -*-
"""
Module containing actions for deleting attributes or sub-elements from the XML
elements because they don't exist anymore in Ape-EAD format.
"""

from lxml import etree
from glamconv.ead.utils import log_element, split_qname
from glamconv.ead.formats import EAD_2002
from glamconv.transformer.actions import TransformAction


ATTR_TO_ERASE = {
    "abbr": (
        "altrender",
        "audience",
        "id",
    ),
    "abstract": (
        "altrender",
        "audience",
        "id",
        "langcode",
    ),
    "accessrestrict": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "accruals": (
        "altrender",
        "audience",
        "id",
    ),
    "acqinfo": (
        "altrender",
        "audience",
        "id",
    ),
    "address": (
        "altrender",
        "audience",
        "id",
    ),
    "addressline": (
        "altrender",
        "audience",
        "id",
    ),
    "altformavail": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "appraisal": (
        "altrender",
        "audience",
        "id",
    ),
    "archdesc": (
        "altrender",
        "audience",
        "id",
    ),
    "arrangement": (
        "altrender",
        "audience",
        "id",
    ),
    "author": (
        "altrender",
        "audience",
        "id",
    ),
    "bibliography": (
        "altrender",
        "audience",
        "id",
    ),
    "bibref": (
        "altrender",
        "audience",
        "encodinganalog",
        "entityref",
        "id",
        "linktype",
    ),
    "bioghist": (
        "altrender",
        "audience",
        "id",
    ),
    "blockquote": (
        "altrender",
        "audience",
        "id",
    ),
    "c": (
        "altrender",
        "tpattern",
    ),
    "c01": (
        "altrender",
        "tpattern",
    ),
    "c02": (
        "altrender",
        "tpattern",
    ),
    "c03": (
        "altrender",
        "tpattern",
    ),
    "c04": (
        "altrender",
        "tpattern",
    ),
    "c05": (
        "altrender",
        "tpattern",
    ),
    "c06": (
        "altrender",
        "tpattern",
    ),
    "c07": (
        "altrender",
        "tpattern",
    ),
    "c08": (
        "altrender",
        "tpattern",
    ),
    "c09": (
        "altrender",
        "tpattern",
    ),
    "c10": (
        "altrender",
        "tpattern",
    ),
    "c11": (
        "altrender",
        "tpattern",
    ),
    "c12": (
        "altrender",
        "tpattern",
    ),
    "change": ("altrender",),
    "colspec": (
        "align",
        "char",
        "charoff",
        "colspec",
        "colwidth",
        "rowsep",
    ),
    "container": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "label",
    ),
    "controlaccess": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "corpname": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "normal",
        "role",
        "rules",
        "source",
    ),
    "creation": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "custodhist": (
        "altrender",
        "audience",
        "id",
    ),
    "dao": (
        "altrender",
        "audience",
        "entityref",
        "id",
        "linktype",
    ),
    "daoloc": (
        "altrender",
        "audience",
        "entityref",
        "id",
        "linktype",
    ),
    "date": (
        "altrender",
        "audience",
        "certainty",
        "id",
        "type",
    ),
    "descrules": ("altrender",),
    "did": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "dimensions": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "label",
    ),
    "dsc": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "othertype",
        "label",
        "tpattern",
    ),
    "ead": (
        "altrender",
        "relatedencoding",
    ),
    "eadheader": (
        "altrender",
        "audience",
        "encodinganalog",
        "findaidstatus",
        "id",
    ),
    "eadid": (
        "encodinganalog",
        "publicid",
        "urn",
    ),
    "emph": (
        "altrender",
        "id",
    ),
    "entry": (
        "align",
        "altrender",
        "audience",
        "char",
        "charoff",
        "colname",
        "colsep",
        "id",
        "morerows",
        "nameend",
        "namest",
        "rowsep",
        "valign",
    ),
    "expan": (
        "altrender",
        "audience",
        "id",
    ),
    "extent": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "label",
        "type",
    ),
    "extptr": (
        "altrender",
        "audience",
        "entityref",
        "id",
        "linktype",
    ),
    "extref": (
        "altrender",
        "audience",
        "entityref",
        "id",
        "linktype",
    ),
    "famname": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "normal",
        "role",
        "rules",
        "source",
    ),
    "filedesc": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "fileplan": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "function": (
        "altrender",
        "audience",
        "authfilenumber",
        "encodinganalog",
        "id",
        "normal",
        "rules",
        "source",
    ),
    "genreform": (
        "altrender",
        "audience",
        "authfilenumber",
        "encodinganalog",
        "id",
        "normal",
        "rules",
        "source",
        "type",
    ),
    "geogname": (
        "altrender",
        "audience",
        "authfilenumber",
        "encodinganalog",
        "id",
        "normal",
        "role",
        "rules",
        "source",
    ),
    "head": (
        "althead",
        "altrender",
        "audience",
        "id",
    ),
    "imprint": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "item": (
        "altrender",
        "audience",
        "id",
    ),
    "label": (
        "altrender",
        "audience",
        "id",
    ),
    "langmaterial": (
        "altrender",
        "audience",
        "id",
        "label",
    ),
    "language": (
        "altrender",
        "audience",
        "id",
    ),
    "langusage": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "legalstatus": ("altrender", "audience", "id", "type"),
    "list": (
        "altrender",
        "audience",
        "continuation",
        "id",
        "mark",
    ),
    "materialspec": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "label",
        "type",
    ),
    "name": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "normal",
        "role",
        "rules",
        "source",
    ),
    "note": (
        "actuate",
        "altrender",
        "audience",
        "id",
        "show",
    ),
    "occupation": (
        "altrender",
        "audience",
        "authfilenumber",
        "encodinganalog",
        "id",
        "normal",
        "rules",
        "source",
    ),
    "odd": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "originalsloc": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "origination": (
        "altrender",
        "audience",
        "id",
    ),
    "otherfindaid": (
        "altrender",
        "audience",
        "id",
    ),
    "p": (
        "altrender",
        "audience",
        "id",
    ),
    "persname": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "normal",
        "role",
        "rules",
        "source",
    ),
    "physdesc": (
        "altrender",
        "audience",
        "id",
        "label",
        "rules",
        "source",
    ),
    "physfacet": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "label",
        "rules",
        "source",
        "unit",
    ),
    "physloc": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "parent",
        "type",
    ),
    "phystech": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "prefercite": (
        "altrender",
        "audience",
        "id",
    ),
    "processinfo": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "profiledesc": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "ptr": (
        "altrender",
        "audience",
        "id",
        "linktype",
    ),
    "publicationstmt": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "publisher": (
        "altrender",
        "audience",
        "id",
    ),
    "ref": (
        "altrender",
        "audience",
        "id",
        "linktype",
    ),
    "relatedmaterial": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "repository": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
        "label",
    ),
    "revisiondesc": ("altrender",),
    "row": (
        "altrender",
        "audience",
        "id",
        "rowsep",
        "valign",
    ),
    "scopecontent": (
        "altrender",
        "audience",
        "id",
    ),
    "separatedmaterial": (
        "altrender",
        "audience",
        "id",
        "type",
    ),
    "seriesstmt": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "sponsor": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "subject": (
        "altrender",
        "audience",
        "authfilenumber",
        "encodinganalog",
        "id",
        "normal",
        "rules",
        "source",
    ),
    "subtitle": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "table": (
        "altrender",
        "audience",
        "colspec",
        "frame",
        "id",
        "pgwide",
        "rowsep",
    ),
    "tbody": (
        "altrender",
        "audience",
        "id",
        "valign",
    ),
    "tgroup": (
        "align",
        "altrender",
        "audience",
        "colsep",
        "id",
        "rowsep",
    ),
    "thead": (
        "altrender",
        "audience",
        "id",
        "valign",
    ),
    "title": (
        "actuate",
        "altrender",
        "arcrole",
        "audience",
        "authfilenumber",
        "encodinganalog",
        "entityref",
        "href",
        "id",
        "linktype",
        "normal",
        "render",
        "role",
        "rules",
        "show",
        "source",
        "title",
        "type",
        "xpointer",
    ),
    "titleproper": (
        "altrender",
        "audience",
        "id",
        "render",
    ),
    "titlestmt": (
        "altrender",
        "audience",
        "encodinganalog",
        "id",
    ),
    "unitdate": (
        "altrender",
        "audience",
        "certainty",
        "datechar",
        "id",
        "label",
        "type",
    ),
    "unitid": (
        "altrender",
        "audience",
        "countrycode",
        "id",
        "identifier",
        "label",
        "repositorycode",
    ),
    "unittitle": (
        "altrender",
        "audience",
        "id",
        "label",
    ),
    "userrestrict": (
        "altrender",
        "audience",
        "id",
    ),
}


def _delete_attributes_and_log(xml_elt, attrs_to_delete, log_data):
    count_elts = 0
    count_atts = 0
    deleted = []
    for attname in xml_elt.attrib:
        if attname in attrs_to_delete:
            deleted.append(attname)
            xml_elt.attrib.pop(attname)
            count_elts = 1
            count_atts += 1
    if len(deleted) > 0:
        msg = f"    Deleted attributes: {' '.join(deleted)}"
        log_data.append(log_element(xml_elt, msg=msg))
    return count_elts, count_atts


def _delete_attributes(xml_elt, attrs_to_delete):
    count_elts = 0
    count_atts = 0
    for attname in xml_elt.attrib:
        if attname in attrs_to_delete:
            xml_elt.attrib.pop(attname)
            count_elts = 1
            count_atts += 1
    return count_elts, count_atts


class AttributesEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "attributes-eraser"
    name = "Erasing attributes that don't exist in Ape-EAD"
    category = "Cleansing"
    desc = (
        "Ape-EAD has more constraints than EAD-2002. Numerous elements "
        "cannot contain some attributes that were authorized in EAD-2002. "
        "This action deletes these attributes."
    )

    def _execute(self, xml_root, logger, log_details):
        count_elts, count_atts = 0, 0
        if log_details:
            log_data = []
            for elt in xml_root.iter(etree.Element):
                namespace, name = split_qname(elt.tag)
                if namespace is not None or len(elt.attrib) == 0:
                    continue
                cnt_e, cnt_a = _delete_attributes_and_log(
                    elt, ATTR_TO_ERASE.get(name, tuple()), log_data
                )
                count_elts += cnt_e
                count_atts += cnt_a
        else:
            for elt in xml_root.iter(etree.Element):
                namespace, name = split_qname(elt.tag)
                if namespace is not None or len(elt.attrib) == 0:
                    continue
                cnt_e, cnt_a = _delete_attributes(elt, ATTR_TO_ERASE.get(name, tuple()))
                count_elts += cnt_e
                count_atts += cnt_a
        if count_elts > 0:
            logger.warning(
                "Deleting non-legit attributes from the elements. "
                f"{count_atts:d} attributes have been deleted from "
                f"{count_elts:d} elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have had some attributes deleted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


def _descgrp_children_move(descgrp_elt, first_following_sibling, log_data):
    count = 1
    if log_data is not None:
        log_data.append(log_element(descgrp_elt))
    last_inserted_note = None
    for child in descgrp_elt.iterchildren(etree.Element):
        nsp, name = split_qname(child.tag)
        if nsp is None and name == "head":
            last_inserted_note = None
        elif nsp is None and name == "descgrp":
            last_inserted_note = None
            count += _descgrp_children_move(child, first_following_sibling)
        elif nsp is None and name == "note":
            last_inserted_note = None
            did_elt = descgrp_elt.find("did")
            if did_elt is None:
                continue
            did_elt.append(child)
        elif nsp is None and name in (
            "address",
            "blockquote",
            "chronlist",
            "list",
            "p",
            "table",
        ):
            if last_inserted_note is None:
                did_elt = descgrp_elt.find("did")
                if did_elt is None:
                    continue
                last_inserted_note = etree.SubElement(did_elt, "note", type="descgrp")
            last_inserted_note.append(child)
        else:
            first_following_sibling.addprevious(child)
    return count


class DescgrpRemover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "descgrp-remover"
    name = "Removing the <descgrp> elements"
    category = "Cleansing"
    desc = (
        "The <descgrp> elements don't exist any more in Ape-EAD. "
        "This action moves their children either into their parent "
        "(<c> or <archdesc>) or into the <did> that exists inside this "
        "parent."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        log_data = None
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//descgrp[not(parent::descgrp)]"):
            count += _descgrp_children_move(elt, elt, log_data)
            elt.getparent().remove(elt)
        if count > 0:
            logger.warning(
                "Removing <descgrp> elements from the <archdesc> and <c> "
                "by moving their child elements inside these <archdesc> or "
                "<c> elements or inside the <did> that exists in these "
                "<archdesc> or <c>. Please note that the <head> from the "
                f"<descgrp> have not been moved. {count:d} <descgrp> elements "
                "have been emptied and deleted."
            )
            if log_details:
                logger.warning(
                    "The following elements have been removed:\n" + "\n".join(log_data)
                )
        return xml_root


ELTS_TO_ERASE = {"heritedcontrolaccess", "runner", "index", "xmlvalue"}


class ElementsEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "elements-eraser"
    name = "Erasing the unknown elements"
    category = "Cleansing"
    desc = (
        "Some elements don't exist in Ape-EAD. "
        "This action deletes them and their content."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for nodename in ELTS_TO_ERASE:
            for node_elt in xml_root.xpath(f".//{nodename}"):
                if log_details:
                    log_data.append(log_element(node_elt, text_content=True))
                node_elt.getparent().remove(node_elt)
                count += 1
        if count > 0:
            logger.warning(f"{count:d} unknown elements have been deleted.")
            if log_details:
                logger.warning(
                    "The following elements have been deleted:\n" + "\n".join(log_data)
                )
        return xml_root
