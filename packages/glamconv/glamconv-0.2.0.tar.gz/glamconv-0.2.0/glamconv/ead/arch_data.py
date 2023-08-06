# -*- coding: utf-8 -*-
"""
Module containing actions for converting or moving XML elements and their
content because they don't exist anymore in Ape-EAD format.
"""

from lxml import etree
from copy import deepcopy
from glamconv.ead.utils import log_element, split_qname
from glamconv.ead.formats import EAD_2002
from glamconv.transformer.actions import TransformAction


class NumberedCConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "numbered-c-converter"
    name = "Converting the <c01>...<c12> into <c>"
    category = "Archive data"
    desc = (
        "The <c01>, ... <c12> elements don't exist anymore in Ape-EAD. "
        "This action converts these elements into <c> elements."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        names = (
            "c01",
            "c02",
            "c03",
            "c04",
            "c05",
            "c06",
            "c07",
            "c08",
            "c09",
            "c10",
            "c11",
            "c12",
        )
        xpath_req = " | ".join(f".//{eltname}" for eltname in names)
        for elt in xml_root.xpath(xpath_req):
            elt.tag = "c"
            if log_details:
                log_data.append(log_element(elt))
            count += 1
        if count > 0:
            logger.info(
                "Converting numbered c (<c01>, ... <c12>) elements into "
                f"<c> elements. {count:d} elements have been converted."
            )
            if log_details:
                logger.info(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


def _move_hierarchical_elements_content(xml_elt, first_following_sibling, log_data):
    """
    Move the contents of xml_elt element before first_following_sibling
    element. The content of the sub-elements with the same name as xml_elt are
    also moved before new_loc.
    """
    count = 1
    if log_data is not None:
        log_data.append(log_element(xml_elt))
    elt_name = xml_elt.tag
    head = xml_elt.find("head")
    if head is not None:
        head.tag = "p"
        if len(head) == 0:
            emph = etree.Element("emph", render="bold")
            emph.text = head.text
            head.text = None
            head.append(emph)
        first_following_sibling.addprevious(head)
    for child in xml_elt.xpath("*[not(self::head)]"):
        if child.tag == elt_name:
            count += _move_hierarchical_elements_content(
                child, first_following_sibling, log_data
            )
        else:
            first_following_sibling.addprevious(child)
    xml_elt.getparent().remove(xml_elt)
    return count


class HierarchicalArchEltsCollapser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "hierarchical-arch-elts-collapser"
    name = "Collapsing the hierarchical structure of archive description elements"
    category = "Archive data"
    desc = (
        "The <accessrestrict>, <accruals>, <acqinfo>, <altformavail>, "
        "<appraisal>, <arrangement>, <bibliography>, <bioghist>, "
        "<controlaccess>, <custodhist>, <fileplan>, <odd>, "
        "<originalsloc>, <otherfindaid>, <phystech>, <prefercite>, "
        "<processinfo>, <relatedmaterial>, <scopecontent>, "
        "<separatedmaterial> and <userestrict> elements cannot contain "
        "anymore child elements of their own type (with the same tag "
        "name). This action moves all the content of these child "
        "elements inside the highest level. The hierarchical structure "
        "is therefore flattened."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        log_data = None
        if log_details:
            log_data = []
        names = (
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
            "fileplan",
            "odd",
            "originalsloc",
            "otherfindaid",
            "phystech",
            "prefercite",
            "relatedmaterial",
            "processinfo",
            "scopecontent",
            "separatedmaterial",
            "userestrict",
        )
        xpath_req = " | ".join(
            f".//{eltname}[not(ancestor::{eltname})]" for eltname in names
        )
        for elt in xml_root.xpath(xpath_req):
            _, eltname = split_qname(elt.tag)
            for sub_elt in elt.xpath(f"{eltname}"):
                count += _move_hierarchical_elements_content(sub_elt, sub_elt, log_data)
        if count > 0:
            logger.warning(
                "Collapsing hierarchical sub-elements for archive "
                f"description into the highest level element. {count:d} "
                "elements have had their content moved in the highest level "
                "element."
            )
            if log_details:
                logger.warning(
                    "The following elements have been collapsed:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class ArchEltsLinksInPMover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "arch-elts-links-in-p-mover"
    name = (
        "Moving the links of <separatedmaterial> <relatedmaterial> "
        "<otherfindaid> in paragraphs"
    )
    category = "Archive data"
    desc = (
        "In Ape-EAD, the <otherfindaid>, <relatedmaterial> and "
        "<separatedmaterial> elements cannot contain anymore child "
        "elements that describe a link (<archref>, <bibref>, <extref>, "
        "<ref>). This action moves these link elements inside a "
        "paragraph (<p>)"
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        names = (
            "archref",
            "bibref",
            "extref",
            "ref",
        )
        parents = (
            "otherfindaid",
            "relatedmaterial",
            "separatedmaterial",
        )
        xpath_pred = " or ".join(f"parent::{prtname}" for prtname in parents)
        xpath_req = " | ".join(f".//{eltname}[{xpath_pred}]" for eltname in names)
        for elt in xml_root.xpath(xpath_req):
            p = etree.Element("p")
            elt.addprevious(p)
            p.append(elt)
            if log_details:
                log_data.append(log_element(p, text_content=True))
            count += 1
        if count > 0:
            logger.info(
                f"Moving links into paragraphs. {count:d} <p> elements have "
                "been created."
            )
            if log_details:
                logger.info(
                    "The following elements have been created:\n" + "\n".join(log_data)
                )
        return xml_root


class ArchdescCNoteInDidMover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "archdesc-c-note-in-did-mover"
    name = "Moving the <note> located in a <c> or an <archdesc> into a <did>"
    category = "Archive data"
    desc = (
        "In Ape-EAD, the <c> and the <archdesc> elements cannot contain "
        "any <note> child element. If such a child element exist, this "
        "action moves this <note> inside the <did> child of <c> or "
        "<archdesc>."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath = " | ".join(
            f".//{hostname}/{nodename}"
            for nodename in ("note", "origination")
            for hostname in ("c", "archdesc")
        )
        for note in xml_root.xpath(xpath):
            parent = note.getparent()
            did = parent.find("did")
            if did is None:
                continue
            did.append(note)
            if log_details:
                log_data.append(log_element(note, text_content=True))
            count += 1
        if count > 0:
            logger.info(
                "Moving <note> elements located in an <archdesc> or a <c> "
                "element, into their sibling <did> (child of <archdesc> or "
                f"<c>). {count:d} elements have been moved."
            )
            if log_details:
                logger.info(
                    "The following elements have been moved:\n" + "\n".join(log_data)
                )
        return xml_root


class DidAbstractConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "did-abstract-converter"
    name = "Converting the <abstract> in <did> into <note>"
    category = "Archive data"
    desc = (
        "In Ape-EAD, the <abstract> elements can't exist in the <did> "
        "elements. This action converts these abstracts into <p> in "
        "<note> elements. Further actions will convert the abstract "
        "children in order to meet the constraints of Ape-EAD related "
        "to <p> elements."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//did/abstract"):
            note = etree.Element("note")
            elt.addprevious(note)
            for attr in elt.attrib:
                note.set(attr, elt.attrib.pop(attr))
            elt.tag = "p"
            note.append(elt)
            if "type" not in note.attrib:
                note.set("type", "abstract")
            elif "label" not in note.attrib:
                note.set("label", "abstract")
            if log_details:
                log_data.append(log_element(note, text_content=True))
            count += 1
        if count > 0:
            logger.warning(
                "Converting <abstract> elements inside <did> into <p> "
                f"elements inserted in <note>. {count:d} elements have been "
                "converted."
            )
            if log_details:
                logger.warning(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class UnittitleUnitdateInDidCopier(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "unittitle-unitdate-in-did-copier"
    name = "Copying <unitdate> located in a <unittitle> in parent <did>"
    category = "Archive data"
    desc = (
        "In Ape-EAD, the <unittitle> elements cannot contain <unitdate> "
        "elements so these date markers will be suppressed by another "
        "cleaning action. In order to keep the date marker, if a "
        "<unitdate> occurs in a <unittitle> and this <unittitle> is "
        "inside a <did> element, this action copies the <unitdate> "
        "inside this <did> if it hasn't already got a <unitdate>."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for unitdate in xml_root.xpath(
            ".//unitdate[parent::unittitle/parent::did[not(unitdate)]]"
        ):
            unittitle = unitdate.getparent()
            did = unittitle.getparent()
            new_date = deepcopy(unitdate)
            new_date.tail = None
            did.append(new_date)
            if log_details:
                log_data.append(log_element(new_date, text_content=True))
            count += 1
        if count > 0:
            logger.info(
                "Copying <unitdate> elements located in a <unittitle> "
                "element, inside the upper-level <did> element that did not "
                f"have a <unitdate>. {count:d} elements have been copied."
            )
            if log_details:
                logger.info(
                    "The following elements have been copied:\n" + "\n".join(log_data)
                )
        return xml_root


class IncorrectNormalDateError(Exception):
    pass


# Dates can be: "21001231", "2100-12-31", "2100-12", "2100",
# "21001231/-19001201", "2100-12-31/-1900-12-01", "2100-12/-1900-12",
# ""2100/-1900" and all the mixed combinations around the "/".
#
# The regular expresssion engine of Python doesn't always give the same
# results as the one of XML Schema. So we're going back to actual Python code.
class IncorrectNormalDateEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "incorrect-normal-date-eraser"
    name = "Deleting incorrect normalized dates"
    category = "Cleansing"
    desc = (
        "This action deletes normalized values in the <unitdate> and "
        "the <date> elements when they don't conform with the expected "
        "format."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        xpath_req = ".//unitdate[@normal] | .//date[@normal]"
        for date_elt in xml_root.xpath(xpath_req):
            norm_date = date_elt.attrib.get("normal", "")
            try:
                if norm_date.strip() == "" or norm_date.strip()[-1] == "/":
                    raise IncorrectNormalDateError()
                parts = norm_date.split("/")
                if len(parts) > 2:
                    raise IncorrectNormalDateError()
                for part in parts:
                    if len(part) == 0:
                        raise IncorrectNormalDateError()
                    if part[0] == "-":
                        part = part[1:]
                    if "-" not in part:
                        if len(part) == 4:
                            elts = (part,)
                        elif len(part) == 8:
                            elts = (part[:4], part[4:6], part[6:])
                        else:
                            raise IncorrectNormalDateError()
                    else:
                        elts = part.split("-")
                    if len(elts) < 1 or len(elts) > 3:
                        raise IncorrectNormalDateError()
                    length = {0: 4, 1: 2, 2: 2}
                    valmin = {0: 0, 1: 1, 2: 1}
                    valmax = {0: 2999, 1: 12, 2: 31}
                    for idx, elt in enumerate(elts):
                        if " " in elt or len(elt) != length[idx] or not elt.isdigit():
                            raise IncorrectNormalDateError()
                        if int(elt) < valmin[idx] or int(elt) > valmax[idx]:
                            raise IncorrectNormalDateError()
            except IncorrectNormalDateError:
                date_elt.attrib.pop("normal")
                count += 1
                if log_details:
                    msg = f"    Deleted value: {norm_date}"
                    log_data.append(log_element(date_elt, msg=msg))
        if count > 0:
            logger.warning(
                "Deleting the 'normal' attribute in the date elements "
                "because its value doesn't conform with the expected format. "
                f"{count:d} elements have had their attribute deleted."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root
