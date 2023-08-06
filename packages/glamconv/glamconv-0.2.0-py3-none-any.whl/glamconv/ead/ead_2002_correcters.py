# -*- coding: utf-8 -*-
"""
Module containing actions for correcting XML elements that don't meet the
constraints described in EAD 2002 format.
"""

import re
from itertools import chain

from lxml import etree

from glamconv.ead.utils import log_element, split_qname
from glamconv.ead.formats import EAD_2002
from glamconv.transformer.actions import TransformAction


class ChangeChildrenOrderer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "change-children-orderer"
    name = "Ordering <change> children"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, the children of <change> must occur in a given order "
        "(first the <date>, then the <item> elements)."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath_req = ".//change[date/preceding-sibling::*]"
        for change in xml_root.xpath(xpath_req):
            if log_details:
                log_data.append(log_element(change))
            count += 1
            # Puts the only <date> at beginning
            for date_elt in change.xpath("date[preceding-sibling::*]"):
                change.insert(0, date_elt)
        if count > 0:
            logger.info(
                f"Re-ordering children in <change> elements. {count:d} "
                "elements have been corrected."
            )
            if log_details:
                logger.info(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class EadheaderChildrenOrderer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "eadheader-children-orderer"
    name = "Ordering <eadheader> children"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, the children of <eadheader> must occur in a given order "
        "(first the <eadid>, then <filedesc>, then <profiledesc>?, "
        "then <revisiondesc>?)."
    )

    def _execute(self, xml_root, logger, log_details):
        eadheader = xml_root.find("eadheader")
        if eadheader is None:
            return xml_root
        count = 0
        if log_details:
            log_data = []
        for nodename in ("revisiondesc", "profiledesc", "filedesc", "eadid"):
            node = eadheader.find(nodename)
            if node is not None:
                eadheader.insert(0, node)
                if log_details:
                    log_data.append(log_element(node))
                count += 1
        if count > 0:
            logger.info(
                f"Re-ordering children in <eadheader> element. {count:d} "
                "elements have been moved."
            )
            if log_details:
                logger.info(
                    "The following elements have been moved:\n" + "\n".join(log_data)
                )
        return xml_root


class ArchdescChildrenOrderer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "archdesc-children-orderer"
    name = "Ordering <archdesc> children"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, the children of <archdesc> must occur in a given order "
        "(first the <did>, then the archive descriptive elements and then "
        "the <dsc>). This action puts the children in the expected order. "
        "This action can be applied to correct EAD trees that are not "
        "valid against the EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath_req = (
            ".//archdesc[ "
            "  did/preceding-sibling::* or "
            "  dsc/following-sibling::*[not(self::dsc)] "
            "]"
        )
        for elt in xml_root.xpath(xpath_req):
            if log_details:
                log_data.append(log_element(elt))
            count += 1
            # Puts the only <did> at beginning
            for did in elt.xpath("did[preceding-sibling::*]"):
                elt.insert(0, did)
            # Puts last elements before all <dsc>
            dsc = elt.find("dsc")
            for subelt in elt.xpath("*[not(self::dsc) and preceding-sibling::dsc]"):
                dsc.addprevious(subelt)
        if count > 0:
            logger.info(
                f"Re-ordering children in <archdesc> elements. {count:d} "
                "elements have been corrected."
            )
            if log_details:
                logger.info(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class CChildrenOrderer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "c-children-orderer"
    name = "Ordering <c> children"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, the children of <c> must occur in a given order (first "
        "the <did>, then the elements for archive description and then "
        "the <c>). This action puts the children in the expected order."
        "This action can be applied to correct EAD trees that are not "
        "valid against the EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath_req = (
            ".//c["
            "  did/preceding-sibling::* or "
            "  c/following-sibling::*[not(self::c)]"
            "]"
        )
        for elt in xml_root.xpath(xpath_req):
            count += 1
            if log_details:
                log_data.append(log_element(elt))
            # Puts the only <did> at beginning
            for did in elt.xpath("did[preceding-sibling::*]"):
                elt.insert(0, did)
            # Puts last elements before all <c>
            c = elt.find("c")
            for subelt in elt.xpath("*[not(self::c) and preceding-sibling::c]"):
                c.addprevious(subelt)
        if count > 0:
            logger.info(
                f"Re-ordering children in <c> elements. {count:d} "
                "elements have been corrected."
            )
            if log_details:
                logger.info(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


EMPTY_ELTS_TO_ERASE = (
    "address",
    "c",
    "change",
    "did",
    "list",
    "notestmt",
    "profiledesc",
    "revisiondesc",
    "table",
)

# elements accepting <p> as child for the inner text
EMPTY_ELTS_WITH_TEXT_TO_WRAP_IN_P = (
    "accessrestrict",
    "accruals",
    "acqinfo",
    "altformavail",
    "appraisal",
    "arrangement",
    "bibliography",
    "bioghist",
    "controlaccess",
    "custodhist",
    "descgrp",
    "dsc",
    "fileplan",
    "note",
    "odd",
    "originalsloc",
    "otherfindaid",
    "publicationstmt",
    "phystech",
    "prefercite",
    "processinfo",
    "relatedmaterial",
    "scopecontent",
    "separatedmaterial",
    "seriesstmt",
    "userestrict",
)


class EmptyEltsEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "empty-elts-eraser"
    name = "Erasing empty elements"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, numerous elements must have at least one child. This "
        "action erases those elements that don't have any child element. "
        "Some elements accept a paragraph (<p>) with textual content. In "
        "these elements, if they are empty but contain a textual content, a "
        "child <p> is added to wrap the text. This action can be applied to "
        "correct EAD trees that are not valid against the EAD-2002 format."
    )

    def _execute(self, xml_root, logger, log_details):
        count_1 = 0
        count_2 = 0
        if log_details:
            log_data_1 = []
            log_data_2 = []
        xpath_req_1 = " | ".join(
            chain(
                (f".//{eltname}[not(*)]" for eltname in EMPTY_ELTS_TO_ERASE),
                (
                    f".//{eltname}[not(*) and normalize-space(text()) = '']"
                    for eltname in EMPTY_ELTS_WITH_TEXT_TO_WRAP_IN_P
                ),
            )
        )
        for elt in xml_root.xpath(xpath_req_1):
            count_1 += 1
            if log_details:
                log_data_1.append(log_element(elt))
            elt.getparent().remove(elt)
        xpath_req_2 = " | ".join(
            f".//{eltname}[not(*)]" for eltname in EMPTY_ELTS_WITH_TEXT_TO_WRAP_IN_P
        )
        for elt in xml_root.xpath(xpath_req_2):
            count_2 += 1
            if log_details:
                log_data_2.append(log_element(elt))
            child = etree.SubElement(elt, "p")
            child.text = elt.text
            elt.text = None
        if count_1 > 0:
            logger.warning(f"{count_1:d} empty elements have been deleted.")
            if log_details:
                logger.warning(
                    "The following empty elements have been deleted:\n"
                    + "\n".join(log_data_1),
                )
        if count_2 > 0:
            logger.warning(
                f"{count_2:d} textual contents in empty elements "
                "have been wrapped in <p> elements."
            )
            if log_details:
                logger.warning(
                    "The texts in the following empty elements have been "
                    "wrapped in <p> elements:\n" + "\n".join(log_data_2),
                )
        return xml_root


ONE_CONTENT_CHILD_ELTS = (
    "accessrestrict",
    "accruals",
    "acqinfo",
    "altformavail",
    "appraisal",
    "arrangement",
    "bibliography",
    "bioghist",
    "controlaccess",
    "custodhist",
    "descgrp",
    "dsc",
    "fileplan",
    "odd",
    "originalsloc",
    "otherfindaid",
    "phystech",
    "prefercite",
    "processinfo",
    "relatedmaterial",
    "scopecontent",
    "separatedmaterial",
    "seriesstmt",
    "userestrict",
)


class ParagraphAdder(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "paragraph-adder"
    name = "Adding paragraph in elements with only a <head>"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, numerous elements must have at least one child element "
        "other than <head>. This action adds an empty paragraph (<p>) "
        "in the elements that don't have such a child element. "
        "This action can be applied to correct EAD trees that are not "
        "valid against the EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath_req = " | ".join(
            f".//{name}[not(*[not(self::head)])]" for name in ONE_CONTENT_CHILD_ELTS
        )
        for elt in xml_root.xpath(xpath_req):
            count += 1
            if log_details:
                log_data.append(log_element(elt, text_content=True))
            etree.SubElement(elt, "p")
        if count > 0:
            logger.warning(
                f"In {count:d} elements, an empty paragraph has been "
                'added in order to have at least one "content" '
                "child."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root


EMPTY_ATTRS_TO_ERASE = {
    "c": ("level",),
    "c01": ("level",),
    "c02": ("level",),
    "c03": ("level",),
    "c04": ("level",),
    "c05": ("level",),
    "c06": ("level",),
    "c07": ("level",),
    "c08": ("level",),
    "c09": ("level",),
    "c10": ("level",),
    "c11": ("level",),
    "c12": ("level",),
}


class EmptyAttrsEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "empty-attrs-eraser"
    name = "Erasing empty attributes"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, some attributes must have a value taken from a "
        "vocabulary. This action erases these attributes that are empty."
        "This action can be applied to correct EAD trees that are not "
        "valid against the EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        count_atts = 0
        count_elts = 0
        if log_details:
            log_data = []
        xpath_reqs = []
        for eltname, attnames in EMPTY_ATTRS_TO_ERASE.items():
            xpath_pred = " or ".join(
                f'@{name}[normalize-space(text())=""]' for name in attnames
            )
            xpath_reqs.append(f".//{eltname}[{xpath_pred}]")
        for elt in xml_root.xpath(" | ".join(xpath_reqs)):
            count_elts += 1
            if log_details:
                deleted = []
            for attname in EMPTY_ATTRS_TO_ERASE[split_qname(elt.tag)[1]]:
                value = elt.attrib.pop(attname, None)
                if value is not None:
                    count_atts += 1
                    if log_details:
                        deleted.append(attname)
            if log_details:
                msg = f"    Deleted attributes: {' '.join(deleted)}"
                log_data.append(log_element(elt, msg=msg))
        if count_elts > 0:
            logger.warning(
                f"{count_atts:d} empty attributes have been deleted from "
                f"{count_elts:d} elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have had some attributes deleted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class IdentifierConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "identifier-converter"
    name = "Converting identifier attributes"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, except in <eadid> and <unitid>, the identifier must be "
        "defined in an 'id' attribute. In <eadid> and <unitid>, it must "
        "be defined in an 'identifier' attribute. Depending on the "
        "element, this action renames the 'identifier' attribute in 'id' "
        "(if there is not already an 'id' attribute) and the 'id' "
        "attribute in 'identifier' (if there is not already an "
        "'identifier' attribute). This action can be applied to correct "
        "EAD trees that are not valid against the EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        # identifier to id
        count1 = 0
        count2 = 0
        if log_details:
            log_data1 = []
            log_data2 = []
        for elt in xml_root.xpath(
            './/*[namespace-uri() = "" '
            "     and not(self::unitid|self::eadid) "
            "     and @identifier]"
        ):
            if "id" not in elt.attrib:
                elt.set("id", elt.attrib.pop("identifier"))
                count1 += 1
                if log_details:
                    log_data1.append(log_element(elt, attributes=("id",)))
            else:
                count2 += 1
                if log_details:
                    log_data2.append(
                        log_element(
                            elt,
                            attributes=(
                                "id",
                                "identifier",
                            ),
                        )
                    )
                elt.attrib.pop("identifier")
        if count1 > 0:
            logger.warning(
                f"{count1:d} elements have had an 'id' attribute "
                "defined from their 'identifier' attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data1)
                )
        if count2 > 0:
            logger.warning(
                f"{count2:d} elements have had their 'identifier' "
                "attribute deleted because they already had an "
                "'id' attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data2)
                )
        # id to identifier
        count1 = 0
        count2 = 0
        if log_details:
            log_data1 = []
            log_data2 = []
        for elt in xml_root.xpath(".//*[(self::unitid|self::eadid) and @id]"):
            if "identifier" not in elt.attrib:
                elt.set("identifier", elt.attrib.pop("id"))
                count1 += 1
                if log_details:
                    log_data1.append(log_element(elt, attributes=("identifier",)))
            else:
                count2 += 1
                if log_details:
                    log_data2.append(
                        log_element(
                            elt,
                            attributes=(
                                "id",
                                "identifier",
                            ),
                        )
                    )
                elt.attrib.pop("id")
        if count1 > 0:
            logger.warning(
                f"{count1:d} elements have had an 'identifier' attribute "
                "defined from their 'id' attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data1),
                )
        if count2 > 0:
            logger.warning(
                f"{count2:d} elements have had their 'id' attribute "
                "deleted because they already had an 'identifier' "
                "attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data2)
                )
        return xml_root


class UnitdateCertainlyConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "unitdate-certainly-converter"
    name = "Converting certainly attribute of <unitdate>"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, the attribute for describing the certainty of a "
        "<unitdate> is 'certainty'. This action corrects the name of this "
        "attribute when it is mispelled 'certainly'. This action can be "
        "applied to correct EAD trees that are not valid against the "
        "EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//unitdate[@certainly]"):
            elt.set("certainty", elt.attrib.pop("certainly"))
            count += 1
            if log_details:
                log_data.append(
                    log_element(elt, attributes=("certainty",), text_content=True)
                )
        if count > 0:
            logger.warning(
                f"{count:d} elements have had a 'certainty' attribute "
                "defined from their 'certainly' attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class COTHERlevelConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "c-OTHERlevel-converter"
    name = "Converting OTHERlevel attribute of <c>"
    category = "EAD 2002 correction"
    desc = (
        "In EAD, the attribute for describing the other level inside a "
        "<c> is 'otherlevel'. This action corrects the name of this "
        "attribute when it is mispelled 'OTHERlevel'. This action can be "
        "applied to correct EAD trees that are not valid against the "
        "EAD-2002 standard."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//c[@OTHERlevel]"):
            elt.set("otherlevel", elt.attrib.pop("OTHERlevel"))
            count += 1
            if log_details:
                log_data.append(log_element(elt, attributes=("otherlevel",)))
        if count > 0:
            logger.warning(
                f"{count:d} elements have had an 'otherlevel' attribute "
                "defined from their 'OTHERlevel' attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class LowercaseElements(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "lowercase-elts"
    name = "lowercase elements"
    category = "EAD 2002 correction"
    desc = "In EAD, all elements should be lowercase."

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for node in xml_root.getiterator():
            if node.tag is etree.Comment:
                continue
            if not node.tag.islower():
                count += 1
                if log_details:
                    log_data.append(log_element(node))
            node.tag = node.tag.lower()
        if count > 0:
            logger.warning(f"{count:d} elements got lowercased")
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


VALID_ID_RGX = re.compile("[_a-z][_a-z0-9.:-]*", re.I | re.U)


def normalize_xml_id(xml_id):
    """try to build a valid xml identifier out of ``xml_id``"""
    chunks = (x.strip() for x in xml_id.split())
    chunks = (x for x in chunks if x != "-")
    xml_id = "-".join(chunks)
    if xml_id and xml_id[0].isdigit():
        xml_id = "_" + xml_id
    return xml_id


class NormalizeIdAttributes(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "normalize-id"
    name = "normalize id attributes"
    category = "EAD 2002 correction"
    desc = "normalize id attributes."

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for node in xml_root.xpath(".//*[@id]"):
            current_id = node.get("id")
            if VALID_ID_RGX.match(current_id) is None:
                normalized_id = normalize_xml_id(current_id)
                if normalized_id:
                    node.attrib["id"] = normalized_id
                else:
                    node.attrib.pop("id")
                count += 1
                if log_details:
                    log_data.append(log_element(node))
            node.tag = node.tag.lower()
        if count > 0:
            logger.warning(f"{count:d} id attributes got normalized")
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root
