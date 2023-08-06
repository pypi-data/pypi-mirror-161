# -*- coding: utf-8 -*-
"""
Module containing actions for converting, moving or correcting XML elements
that occur inside the header or the front-matter.
"""

from lxml import etree

from glamconv.ead.utils import log_element, insert_child_at_element_beginning
from glamconv.ead.formats import EAD_2002
from glamconv.transformer.actions import TransformAction
from glamconv.transformer.parameters import SingleParameter


class IdentifiersDefiner(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "identifiers-definer"
    name = "Defining identifiers"
    category = "Header"
    desc = (
        "This action defines the identifiers inside the <eadid> element, "
        "if they are not already defined."
    )
    params_def = (
        SingleParameter(
            "country_code",
            "Country code",
            "Code of the country where dwells the organization that "
            "publishes the EAD. Only some codes are allowed. They are in "
            "upper case and contain two letters.",
            "Text",
            str,
            "",
        ),
        SingleParameter(
            "agency_code",
            "Agency code",
            "Code of the organization that publishes the EAD. The codes are "
            "actually in upper case and begin with the country code.",
            "Text",
            str,
            "",
        ),
        SingleParameter(
            "document_id",
            "Document identifier",
            "Identifier of the document. The identifier usually starts with "
            "the agency code.",
            "Text",
            str,
            "",
        ),
        SingleParameter(
            "favour_xml_document_id",
            "Favour XML data for document identifier",
            "If the 'identifier' attribute of <eadid> element is not "
            "defined, it is possible either to gather data from the XML to "
            "build it (typically the text inside the <eadid> element) or to "
            'use the value given in the "Document identifier" parameter '
            "of this action. When this parameter is set, this action will "
            "first try to use the XML data to build the document identifier "
            "and will only use the parameter value if no XML data can be "
            "found. When this parameter is unset, this action will always "
            "use the parameter value without using the XML data.",
            "Boolean",
            bool,
            False,
        ),
    )

    def _execute(
        self,
        xml_root,
        logger,
        log_details,
        country_code,
        agency_code,
        document_id,
        favour_xml_document_id,
    ):
        for eadid in xml_root.xpath(".//eadid"):
            if country_code and country_code.upper() != "FR":
                logger.info("ignoring specified country code %s", country_code.upper())
            eadid.set("countrycode", "FR")
            if agency_code != "":
                eadid.set("mainagencycode", agency_code)
                logger.info(
                    "Setting the 'mainagencycode' attribute in the <eadid> "
                    f"element\n    New value: {agency_code}"
                )
            xml_built_id = (eadid.text or "").strip()
            if document_id != "" and (
                not (favour_xml_document_id) or len(xml_built_id) == 0
            ):
                eadid.set("identifier", document_id)
                logger.info(
                    "Setting the 'identifier' attribute in the <eadid> "
                    "element from the document_id parameter\n   New value: "
                    f"{document_id}"
                )
            elif (
                favour_xml_document_id
                and len(xml_built_id) > 0
                and "identifier" not in eadid.attrib
            ):
                eadid.set("identifier", xml_built_id)
                logger.info(
                    "Setting the 'identifier' attribute in the <eadid> "
                    "element from the XML data read in <eadid>\n   New "
                    f"value: {xml_built_id}"
                )
        return xml_root


def _add_content_to_odd_elt(xml_root, elements, title, log_data):
    count = 0
    odd_lst = xml_root.xpath(".//archdesc[1]/odd")
    if len(odd_lst) > 0:
        odd = odd_lst[0]
    else:
        odd = etree.Element("odd")
        dsc_lst = xml_root.xpath(".//archdesc[1]/dsc")
        if len(dsc_lst) > 0:
            dsc_lst[0].addprevious(odd)
        else:
            xml_root.xpath(".//archdesc[1]")[0].append(odd)
    if title != "":
        p = etree.SubElement(odd, "p")
        emph = etree.SubElement(p, "emph")
        emph.set("render", "bold")
        emph.text = title
    for elt in elements:
        odd.append(elt)
        if log_data is not None:
            log_data.append(log_element(elt, text_content=True))
        count += 1
    return count


class EditionstmtConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "editionstmt-converter"
    name = "Moving the content of <editionstmt> into <odd>"
    category = "Header"
    desc = (
        "The <editionstmt> element doesn't exist anymore. This action "
        "moves its content into the <processinfo> element of the "
        "<archdesc> element. The couples <edition> / <p> in <editionstmt>"
        "are transformed into list items before being moved in <odd>."
    )
    params_def = (
        SingleParameter(
            "title",
            "Title",
            "Title inserted in the <odd> element before the <editionstmt> content.",
            "Text",
            str,
            "Editions",
        ),
    )

    def _execute(self, xml_root, logger, log_details, title):
        count = 0
        log_data = None
        if log_details:
            log_data = []
        list_elt = etree.Element("list")
        for edt in xml_root.xpath(".//editionstmt/edition"):
            nxt = edt.xpath("following-sibling::*")
            if len(nxt) == 0 or nxt[0].tag != "p":
                itm = etree.Element("item")
            else:
                itm = nxt[0]
                itm.tag = "item"
            list_elt.append(itm)
            emph = etree.Element("emph", render="bold")
            emph.text = edt.text.strip()
            emph.tail = ": "
            insert_child_at_element_beginning(itm, emph)
        if len(list_elt) > 0:
            count += _add_content_to_odd_elt(xml_root, [list_elt], title, log_data)
            logger.warning(
                "Moving the content of <editionstmt> elements into the <odd> "
                f"element in <archdesc>. {count:d} elements have been inserted "
                "in <odd>"
            )
            if log_details:
                logger.warning(
                    "The following elements have been inserted in <odd>:\n"
                    + "\n".join(log_data)
                )
        for stmt in xml_root.xpath(".//editionstmt"):
            stmt.getparent().remove(stmt)
        return xml_root


class NotestmtConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "notestmt-converter"
    name = "Moving the content of <notestmt> into <odd>"
    category = "Header"
    desc = (
        "The <notestmt> element doesn't exist anymore. This action moves "
        "its content into the <odd> element in <archdesc>. The <note> "
        "elements inside <notestmt> are inserted into <p> and then moved "
        "inside <odd> (as Ape-EAD doesn't allow the notes inside odd)."
    )
    params_def = (
        SingleParameter(
            "title",
            "Title",
            "Title inserted in the <odd> element before the <notestmt> content.",
            "Text",
            str,
            "Notes",
        ),
    )

    def _execute(self, xml_root, logger, log_details, title):
        count = 0
        log_data = None
        if log_details:
            log_data = []
        elts_to_move = []
        for note in xml_root.xpath(".//notestmt/note"):
            p = etree.Element("p")
            p.append(note)
            elts_to_move.append(p)
        if len(elts_to_move) > 0:
            count += _add_content_to_odd_elt(xml_root, elts_to_move, title, log_data)
            logger.warning(
                "Moving the content of <notestmt> elements into the <odd> "
                f"element in <archdesc>. {count:d} elements have been inserted "
                "in <odd>"
            )
            if log_details:
                logger.warning(
                    "The following elements have been inserted in <odd>:\n"
                    + "\n".join(log_data)
                )
        for stmt in xml_root.xpath(".//notestmt"):
            stmt.getparent().remove(stmt)
        return xml_root


def _div_collapser(div_elt, elts_to_move, level=0):
    head = div_elt.find("head")
    if head is not None:
        head.text = ("> " * level) + (head.text or "")
        head.tag = "p"
        if len(head) == 0:
            emph = etree.Element("emph", render="italic")
            emph.text = head.text
            head.text = None
            head.append(emph)
        elts_to_move.append(head)
    for child in div_elt.xpath("*[not(self::head)]"):
        if child.tag == "div":
            _div_collapser(child, elts_to_move, level + 1)
        else:
            elts_to_move.append(child)


class FrontmatterConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "frontmatter-converter"
    name = "Moving the content of <frontmatter> into <odd>"
    category = "Header"
    desc = (
        "The <frontmatter> element doesn't exist anymore in Ape-EAD. This "
        "action moves its content into the <odd> element in <archdesc> "
        "element. Be aware that the <titlepage> sub-element is not moved "
        "and thus is deleted."
    )
    params_def = (
        SingleParameter(
            "title",
            "Title",
            "Title inserted in the <odd> element before the <frontmatter> content.",
            "Text",
            str,
            "Prolegomena",
        ),
    )

    def _execute(self, xml_root, logger, log_details, title):
        count = 0
        log_data = None
        if log_details:
            log_data = []
        elts_to_move = []
        for div in xml_root.xpath(".//frontmatter/div"):
            _div_collapser(div, elts_to_move)
        if len(elts_to_move) > 0:
            count += _add_content_to_odd_elt(xml_root, elts_to_move, title, log_data)
            logger.warning(
                "Moving the content of <frontmatter> elements into the <odd> "
                f"element in <archdesc> (except <titlepage>). {count:d} "
                "elements have been inserted in <odd>"
            )
            if log_details:
                logger.warning(
                    "The following elements have been inserted in <odd>:\n"
                    + "\n".join(log_data)
                )
        if log_details:
            for ttpg in xml_root.xpath(".//frontmatter/titlepage"):
                logger.warning(
                    "Deleting <titlepage> element inside <frontmatter>. The "
                    "following sub-elements have been deleted:\n"
                    + log_element(ttpg, text_content=True)
                )
        for ftmtt in xml_root.xpath(".//frontmatter"):
            ftmtt.getparent().remove(ftmtt)
        return xml_root


class SponsorConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "sponsor-converter"
    name = "Moving <sponsor> from <titlestmt> into <odd>"
    category = "Header"
    desc = (
        "In Ape-EAD, the <sponsor> element that could occur in "
        "<titlestmt> doesn't exist anymore. This action transforms it "
        "into a paragraph (<p>) and moves it into the <odd> element in "
        "<archdesc> element."
    )
    params_def = (
        SingleParameter(
            "title",
            "Title",
            "Title inserted in the <odd> element before the <sponsor> content.",
            "Text",
            str,
            "Sponsor: ",
        ),
    )

    def _execute(self, xml_root, logger, log_details, title):
        count = 0
        log_data = None
        if log_details:
            log_data = []
        elts_to_move = []
        for spsr in xml_root.xpath(".//titlestmt/sponsor"):
            spsr.tag = "p"
            emph = etree.Element("emph", render="bold")
            emph.text = title
            emph.tail = " "
            insert_child_at_element_beginning(spsr, emph)
            elts_to_move.append(spsr)
        if len(elts_to_move) > 0:
            count += _add_content_to_odd_elt(xml_root, elts_to_move, title, log_data)
            logger.warning(
                f"{count:d} <sponsor> elements have been moved into the "
                "<odd> element in <archdesc>."
            )
            if log_details:
                logger.warning(
                    "The following elements have been moved:\n" + "\n".join(log_data)
                )
        return xml_root


class StmtPNumEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "stmt-p-num-eraser"
    name = "Erasing <p>, <num> from <publicationstmt>, <seriesstmt> "
    category = "Header"
    desc = (
        "In Ape-EAD, <p> and <num> elements cannot occur inside "
        "<publicationstmt> or <seriestmt> elements. This action deletes "
        "these non-legit child elements."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath_req = (
            ".//publicationstmt/p | .//publicationstmt/num | "
            ".//seriesstmt/p | .//seriesstmt/num"
        )
        for elt in xml_root.xpath(xpath_req):
            count += 1
            if log_details:
                log_data.append(log_element(elt, text_content=True))
            elt.getparent().remove(elt)
        if count > 0:
            logger.warning(
                f"{count:d} <p> and <num> elements have been deleted "
                "from <publicationstmt> and <seriesstmt>."
            )
            if log_details:
                logger.warning(
                    "The following elements have been suppressed:\n"
                    + "\n".join(log_data)
                )
        return xml_root
