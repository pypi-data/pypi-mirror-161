# -*- coding: utf-8 -*-
"""
Module containing actions for converting, moving or correcting XML elements
that contain text data.
"""

from itertools import chain
from lxml import etree
from glamconv.ead.utils import (
    log_element,
    write_hierarchy,
    split_qname,
    insert_text_at_element_end,
    insert_text_before_element,
    adjust_content_in_mixed,
)
from glamconv.ead.formats import EAD_2002
from glamconv.transformer.actions import TransformAction


class AddressConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "address-converter"
    name = "Converting <address> into <p> in non-legit parents"
    category = "Text data"
    desc = (
        "In Ape-EAD, <address> elements can only occur in a few elements. "
        "This action converts the <address> that occur outside these "
        "legit parents into paragraphs (<p>). If the parent element can "
        "only contain text data, this action directly adds the text in "
        "this parent, each line separated by a hyphen. Be aware that in "
        "case of imbricated elements, this action can produce a result "
        "that have imbricated paragraphs (<p>); be sure to execute the "
        "action that removes non-legit paragraphs after this action."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        text_only_parents = (
            "entry",
            "event",
            "extref",
            "extrefloc",
            "ref",
            "refloc",
        )
        parents = (
            "accessrestrict",
            "accruals",
            "acqinfo",
            "altformavail",
            "appraisal",
            "arrangement",
            "bibliography",
            "bioghist",
            "blockquote",
            "controlaccess",
            "custodhist",
            "descgrp",
            "div",
            "dsc",
            "entry",
            "event",
            "extref",
            "extrefloc",
            "fileplan",
            "item",
            "note",
            "odd",
            "originalsloc",
            "otherfindaid",
            "p",
            "phystech",
            "prefercite",
            "processinfo",
            "ref",
            "refloc",
            "relatedmaterial",
            "scopecontent",
            "separatedmaterial",
            "userestrict",
        )
        xpath_req = " | ".join(f".//{name}/address" for name in parents)
        for addr in xml_root.xpath(xpath_req):
            parent = addr.getparent()
            if split_qname(parent.tag)[1] in text_only_parents:
                texts = []
                for adln in addr.iterchildren(etree.Element):
                    adjust_content_in_mixed(adln)
                    texts.append(adln.text)
                insert_text_before_element(addr, " - ".join(texts))
                log_elt = parent
            else:
                p = etree.Element("p")
                addr.addprevious(p)
                for adln in addr.iterchildren(etree.Element):
                    insert_text_at_element_end(p, adln.text)
                    p.extend(adln.getchildren())
                    etree.SubElement(p, "lb")
                if len(p) > 0:
                    p.remove(p[-1])  # Removes last <lb>
                log_elt = p
            parent.remove(addr)
            count += 1
            if log_details:
                log_data.append(log_element(log_elt, text_content=True))
        if count > 0:
            logger.warning(
                f"{count:d} <address> elements have been converted in " "<p> elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


def _gather_children_to_move(elt, elts_to_move):
    for child in elt.iterchildren(etree.Element):
        if child.tag == elt.tag:
            _gather_children_to_move(child, elts_to_move)
        else:
            elts_to_move.append(child)


class BlockquoteRemover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "blockquote-remover"
    name = "Removing <blockquote> elements"
    category = "Text data"
    desc = (
        "The <blockquote> elements don't exist anymore in Ape-EAD. "
        "This action moves their children into the blockquote parent. The "
        "blockquote is therefore removed from the EAD tree but its "
        "content still exits in the tree. When possible, the texts inside "
        "the paragraphs that were in the blockquote are encapsulated "
        'into an <emph render="italic"> element. Be aware that in case '
        "of imbricated elements, this action can produce a result that "
        "have imbricated paragraphs (<p>); be sure to execute the action "
        "that removes non-legit paragraphs after this action."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for blq in xml_root.xpath(".//blockquote[not(parent::blockquote)]"):
            count += 1
            if log_details:
                log_data.append(log_element(blq, text_content=True))
            # Moves the subelements (children) into the blockquote parent
            elts_to_move = []
            _gather_children_to_move(blq, elts_to_move)
            for subelt in elts_to_move:
                # If subelt is an empty paragraph (most of the cases),
                # adds an emph in the paragraph for italizing the text
                if subelt.tag == "p" and len(subelt) == 0:
                    emph = etree.Element("emph", render="italic")
                    emph.text = subelt.text
                    subelt.text = None
                    subelt.append(emph)
                blq.addprevious(subelt)
            # If blockquote has a tail text, inserts it into a paragraph
            if blq.tail is not None and len(blq.tail.strip()) > 0:
                p = etree.Element("p")
                p.text = blq.tail
                blq.tail = None
                blq.addprevious(p)
            # Deletes blockquote
            blq.getparent().remove(blq)
        if count > 0:
            logger.warning(
                f"{count:d} <blockquote> elements have been removed by moving "
                "their child elements into the blockquote parent."
            )
            if log_details:
                logger.warning(
                    "The following elements have been emptied and deleted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class NoteRemover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "note-remover"
    name = "Removing <note> elements in non-legit parents"
    category = "Text data"
    desc = (
        "In Ape-EAD, <note> elements can only occur in a few elements. "
        "This action moves the content of the <note> that occur outside "
        "these legit elements into the note parent. The note is therefore "
        "removed from the EAD tree but its content still exists in the "
        "tree. Be aware that in case of imbricated elements, this action "
        "can produce a result that have imbricated paragraphs (<p>); be "
        "sure to execute the action that removes non-legit paragraphs "
        "after this action."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        parents = (
            "accessrestrict",
            "accruals",
            "acqinfo",
            "altformavail",
            "appraisal",
            "archref",
            "arrangement",
            "bibliography",
            "bioghist",
            "blockquote",
            "controlaccess",
            "custodhist",
            "descgrp",
            "div",
            "dsc",
            "entry",
            "event",
            "extref",
            "extrefloc",
            "fileplan",
            "item",
            "odd",
            "originalsloc",
            "otherfindaid",
            "phystech",
            "prefercite",
            "processinfo",
            "ref",
            "refloc",
            "relatedmaterial",
            "scopecontent",
            "separatedmaterial",
            "userestrict",
        )
        xpath_req = " | ".join(f".//{name}/note" for name in parents)
        for note in xml_root.xpath(xpath_req):
            count += 1
            if log_details:
                log_data.append(log_element(note, text_content=True))
            # Moves the subelements (children) into the note parent
            elts_to_move = []
            _gather_children_to_move(note, elts_to_move)
            for subelt in elts_to_move:
                note.addprevious(subelt)
            # If note has a tail text, inserts it into a paragraph
            if note.tail is not None and len(note.tail.strip()) > 0:
                p = etree.Element("p")
                p.text = note.tail
                note.tail = None
                note.addprevious(p)
            # Deletes note
            note.getparent().remove(note)
        if count > 0:
            logger.warning(
                f"{count:d} <note> elements have been removed by moving their "
                "child elements into the note parent."
            )
            if log_details:
                logger.warning(
                    "The following elements have been emptied and deleted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class ChronlistConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "chronlist-converter"
    name = "Converting <chronlist> into regular lists"
    category = "Text data"
    desc = (
        "In Ape-EAD, the <chronlist> elements don't exist anymore. "
        "This action converts these chronological lists into regular "
        "lists, each item containing the date and the associated "
        "events. If possible, the date is inserted in an "
        '<emph render="bold"> element.'
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for list_elt in xml_root.xpath(".//chronlist"):
            list_elt.tag = "list"
            # Header
            lsthead = list_elt.find("listhead")
            if lsthead is not None:
                new_head = False
                head = list_elt.find("head")
                if head is None:
                    new_head = True
                    head = etree.Element("head")
                for hd_elt in lsthead.iterchildren(etree.Element):
                    if head.text or len(head) > 0:
                        insert_text_at_element_end(head, " / ")
                    insert_text_at_element_end(head, hd_elt.text)
                    head.extend(hd_elt.getchildren())
                if new_head and (head.text or len(head) > 0):
                    list_elt.insert(0, head)
                list_elt.remove(lsthead)
            # Items
            for chritm in list_elt.xpath("chronitem"):
                item = etree.Element("item")
                chritm.addprevious(item)
                date = chritm.find("date")
                if date is None:
                    continue
                if len(date) == 0:
                    emph = etree.Element("emph", render="bold")
                    emph.text = date.text
                    date.text = None
                    date.append(emph)
                insert_text_at_element_end(item, date.text)
                item.extend(date.getchildren())
                for idx, evt in enumerate(chritm.xpath("event|eventgrp/event")):
                    insert_text_at_element_end(item, " : " if idx == 0 else " ; ")
                    insert_text_at_element_end(item, evt.text)
                    item.extend(evt.getchildren())
                list_elt.remove(chritm)
            count += 1
            if log_details:
                log_data.append(log_element(list_elt))
        if count > 0:
            logger.warning(
                f"{count:d} <chronlist> elements have been converted "
                "into regular lists containing <item> elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class DefinitionListConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "def-list-converter"
    name = "Converting <list> with <defitem> children into regular lists"
    category = "Text data"
    desc = (
        "In Ape-EAD, <list> elements can not have <defitem> children. "
        "This action converts these lists into regular lists by "
        "converting the <defitem> children into <item> children. "
        "The content of the <label> child of <defitem> is inserted "
        "at the begining of the <item> child of <defitem>. If possible, "
        'the label is inserted in an <emph render="bold"> element.'
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for list_elt in xml_root.xpath(".//list[defitem]"):
            # Header
            head = etree.Element("head")
            for hd_elt in list_elt.xpath("listhead/*"):
                if head.text or len(head) > 0:
                    insert_text_at_element_end(head, " / ")
                insert_text_at_element_end(head, hd_elt.text)
                head.extend(hd_elt.getchildren())
            if head.text or len(head) > 0:
                list_elt.insert(0, head)
            lsth = list_elt.find("listhead")
            if lsth is not None:
                list_elt.remove(lsth)
            # Items
            for defitm in list_elt.xpath("defitem"):
                label = defitm.find("label")
                item = defitm.find("item")
                if item is None:
                    item = etree.Element("item")
                    defitm.append(item)
                if label is not None and len(label) == 0:
                    emph = etree.Element("emph", render="bold")
                    emph.text = label.text
                    label.text = None
                    label.append(emph)
                insert_text_at_element_end(label, (" : " + (item.text or "")))
                for child in reversed(list(label.getchildren())):
                    item.insert(0, child)
                item.text = label.text
                defitm.addprevious(item)
                list_elt.remove(defitm)
            count += 1
            if log_details:
                log_data.append(log_element(list_elt))
        if count > 0:
            logger.warning(
                f"{count:d} <list> elements containing <defitem> "
                "children have been converted into regular lists "
                "containing <item> elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


def _list_content_extractor(
    list_elt, extracted_elts, prefix="- ", indent="  ", level=0
):
    for child in list_elt.iterchildren(etree.Element):
        if child.tag == "head":
            adjust_content_in_mixed(child)
            emph = etree.Element("emph", render="bold")
            emph.text = child.text
            child.text = indent * level
            child.append(emph)
            extracted_elts.append(child)
            continue
        if child.text or (len(child) > 0 and child[0].tag != "list"):
            child.text = (indent * level) + prefix + (child.text or "")
        sublist = child.find("list")
        while sublist is not None:
            itm = etree.Element(child.tag)
            itm.text = child.text
            child.text = None
            for subelt in reversed(sublist.itersiblings(preceding=True)):
                itm.append(subelt)
            if itm.text or len(itm) > 0:
                extracted_elts.append(itm)
            _list_content_extractor(sublist, extracted_elts, prefix, indent, level + 1)
            child.remove(sublist)
            child.text = sublist.tail
            if child.text or (len(child) > 0 and child[0].tag != "list"):
                child.text = (indent * level) + prefix + (child.text or "")
            sublist = child.find("list")
        if child.text or len(child) > 0:
            extracted_elts.append(child)


class ListConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "list-converter"
    name = "Removing <list> elements in non-legit parents"
    category = "Text data"
    desc = (
        "In Ape-EAD, <list> elements can not occur anymore in some "
        "elements. This action converts each of these lists into a "
        "paragraph (<p>); the items being separated by line breaks "
        "(<lb>). If the parent element can't contain a paragraph, "
        "this action directly adds the text in this parent and "
        "separates each item by a semi-colon. Be aware that in case "
        "of imbricated elements, this action can produce a result that "
        "have imbricated paragraphs (<p>); be sure to execute the action "
        "that removes non-legit paragraphs after this action."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        text_only_parents = ("event", "extref", "extrefloc", "ref", "refloc")
        parents = (
            "controlaccess",
            "descgrp",
            "entry",
            "event",
            "extref",
            "extrefloc",
            "note",
            "p",
            "phystech",
            "ref",
            "refloc",
        )
        xpath_req = " | ".join(f".//{name}/list" for name in parents)
        for list_elt in xml_root.xpath(xpath_req):
            parent = list_elt.getparent()
            if split_qname(parent.tag)[1] in text_only_parents:
                texts = []
                extracted_elts = []
                _list_content_extractor(list_elt, extracted_elts, prefix="", indent="")
                for elt in extracted_elts:
                    adjust_content_in_mixed(elt)
                    texts.append(elt.text)
                insert_text_before_element(list_elt, " ; ".join(texts))
                log_elt = parent
            else:
                p = etree.Element("p")
                list_elt.addprevious(p)
                extracted_elts = []
                _list_content_extractor(list_elt, extracted_elts)
                for idx, elt in enumerate(extracted_elts):
                    if idx != 0:
                        etree.SubElement(p, "lb")
                    insert_text_at_element_end(p, elt.text)
                    p.extend(elt.getchildren())
                log_elt = p
            parent.remove(list_elt)
            count += 1
            if log_details:
                log_data.append(log_element(log_elt, text_content=True))
        if count > 0:
            logger.warning(
                f"{count:d} <list> elements have been converted into " "<p> elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class LegalstatusConverter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "legalstatus-converter"
    name = "Converting the <legalstatus> into <p>"
    category = "Text data"
    desc = (
        "The <legalstatus> elements don't exist in Ape-EAD. This action "
        "converts these elements into paragraphs (<p>)."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for stat in xml_root.xpath(".//legalstatus"):
            stat.tag = "p"
            count += 1
            if log_details:
                log_data.append(log_element(stat, text_content=True))
        if count > 0:
            logger.warning(
                f"{count:d} <legalstatus> elements have been converted "
                "into <p> elements."
            )
            if log_details:
                logger.warning(
                    "The following elements have been converted:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class ParagraphRemover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "paragraph-remover"
    name = "Removing <p> elements in non-legit parents"
    category = "Text data"
    desc = (
        "After executing the actions that removes blockquotes, addresses, "
        "notes, lists or tables, the resulting tree can have paragraphs "
        "that occur in non-legit parents (typically inside another "
        "paragraph). This action removes these paragraphs but keeps their "
        "content and adds a line break (<lb>) at the end of this content."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        for p_elt in xml_root.xpath("p[parent::p]"):
            insert_text_before_element(p_elt, p_elt.text)
            for child in p_elt:
                p_elt.addprevious(child)
            p_elt.addprevious(etree.Element("lb"))
            count += 1
        if count > 0:
            logger.warning(
                f"Removing <p> occuring inside non-legit parents: {count:d} "
                "paragraphs have been removed."
            )
        return xml_root


MIXED_CONTENT = {
    "abstract": tuple(),
    "addressline": tuple(),
    "archref": tuple(),
    "author": tuple(),
    "bibref": (
        "imprint",
        "name",
        "title",
    ),
    "bibseries": tuple(),
    "container": tuple(),
    "corpname": tuple(),
    "creation": ("date",),
    "date": tuple(),
    "descrules": ("extref",),
    "dimensions": tuple(),
    "edition": tuple(),
    "emph": tuple(),
    "entry": tuple(),
    "event": tuple(),
    "extent": tuple(),
    "extref": tuple(),
    "extrefloc": tuple(),
    "famname": tuple(),
    "function": tuple(),
    "genreform": tuple(),
    "geogname": tuple(),
    "head": tuple(),
    "head01": tuple(),
    "head02": tuple(),
    "imprint": (
        "date",
        "geogname",
        "publisher",
    ),
    "item": (
        "emph",
        "extref",
        "lb",
        "list",
    ),
    "label": tuple(),
    "langmaterial": ("language",),
    "language": tuple(),
    "langusage": ("language",),
    "legalstatus": tuple(),
    "materialspec": tuple(),
    "name": tuple(),
    "num": tuple(),
    "occupation": tuple(),
    "origination": (
        "corpname",
        "famname",
        "name",
        "persname",
    ),
    "p": (
        "abbr",
        "emph",
        "expan",
        "extref",
        "lb",
        "note",
    ),
    "persname": tuple(),
    "physdesc": (
        "dimensions",
        "extent",
        "genreform",
        "physfacet",
    ),
    "physfacet": tuple(),
    "physloc": tuple(),
    "publisher": tuple(),
    "ref": tuple(),
    "refloc": tuple(),
    "repository": (
        "address",
        "corpname",
        "extref",
        "name",
    ),
    "resource": tuple(),
    "runner": tuple(),
    "sponsor": tuple(),
    "subarea": tuple(),
    "subject": tuple(),
    "subtitle": (
        "emph",
        "lb",
    ),
    "title": tuple(),
    "titleproper": (
        "emph",
        "lb",
    ),
    "unitdate": tuple(),
    "unitid": (
        "extptr",
        "title",
        "abbr",
        "emph",
        "expan",
        "lb",
    ),
    "unittitle": (
        "abbr",
        "emph",
        "expan",
        "lb",
    ),
}


def _adjust_mixed_content(xml_elt):
    """
    Walk depth-first in the XML tree from ``xml_elt`` and adjust the mixed
    content of the XML element (see ``MIXED_CONTENT`` dictionary to know
    which element can be kept at a given level of the tree).
    """
    count = 0
    child_names = set()
    if len(xml_elt) == 0:
        return 0
    for child in xml_elt.iterchildren(etree.Element):
        child_names.add(split_qname(child.tag)[1])
        # First process the children (process depth-first in the tree)
        count += _adjust_mixed_content(child)
    namespace, name = split_qname(xml_elt.tag)
    to_keep = MIXED_CONTENT.get(name)
    if namespace is not None or to_keep is None:
        # ``xml_elt`` is not in ``MIXED_CONTENT`` and thus doesn't need to be
        # adjusted
        return count
    # If <lb> is not to keep, adds a space
    if "lb" not in to_keep:
        for lb_elt in xml_elt.xpath("lb"):
            lb_elt.tail = " " + (lb_elt.tail or "")
    # Suppress the mixed elements not to be kept
    if len(child_names.difference(set(to_keep))) > 0:
        count += 1
    adjust_content_in_mixed(xml_elt, to_keep)
    return count


def _adjust_mixed_content_and_log(xml_elt):
    if len(xml_elt) == 0:
        return []
    children_log_data = {}
    child_names = set()
    for child in xml_elt.iterchildren(etree.Element):
        _, cname = split_qname(child.tag)
        child_names.add(cname)
        if cname not in children_log_data:
            children_log_data[cname] = []
        children_log_data[cname].extend(_adjust_mixed_content_and_log(child))
    namespace, name = split_qname(xml_elt.tag)
    to_keep = MIXED_CONTENT.get(name)
    if namespace is not None or to_keep is None:
        log_data = list(chain.from_iterable(children_log_data.values()))
        return log_data
    removed = set()
    # If <lb> is not to keep, adds a space
    if "lb" not in to_keep:
        for lb_elt in xml_elt.xpath("lb"):
            lb_elt.tail = " " + (lb_elt.tail or "")
    # Suppress the mixed elements not to be kept
    for cname in child_names.difference(set(to_keep)):
        removed.add(cname)
        for item in children_log_data.pop(cname):
            removed = removed.union(item[1])
    adjust_content_in_mixed(xml_elt, to_keep)
    log_data = [
        (write_hierarchy(xml_elt), removed),
    ]
    log_data.extend(chain.from_iterable(children_log_data.values()))
    return log_data


class MixedContentAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "mixed-content-adjuster"
    name = "Removing the non-legit children in the mixed content elements"
    category = "Text data"
    desc = (
        "In Ape-EAD, the elements with a mixed content (child elements "
        "mixed with text content) have a much more restricted list of "
        "allowed children. This action removes the non-legit children "
        "but keeps their textual content."
    )

    def _execute(self, xml_root, logger, log_details):
        if log_details:
            log_data = _adjust_mixed_content_and_log(xml_root)
            count = len(log_data)
        else:
            count = _adjust_mixed_content(xml_root)
        if count > 0:
            logger.warning(
                f"{count:d} mixed content elements have had some of their "
                "children deleted"
            )
            if log_details:
                log_info = [
                    f"{elt}\n   Removed elements: {', '.join(remov)}"
                    for elt, remov in log_data
                    if len(remov) > 0
                ]
                logger.warning(
                    "The following mixed content elements have been modified:\n"
                    + "\n".join(log_info)
                )
        return xml_root
