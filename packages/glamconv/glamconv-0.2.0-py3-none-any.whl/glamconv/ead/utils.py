# -*- coding: utf-8 -*-
"""
Module defining several useful functions that will be used inside
the transform actions defined in the other modules of this sub-package.
"""

import re


NS = {
    "ead": "urn:isbn:1-931666-22-9",
    "xlink": "http://www.w3.org/1999/xlink",
}


QNAME_PATTERN = re.compile("({.*})?(.+)")


def split_qname(qname):
    namespace, local_name = QNAME_PATTERN.match(qname).groups()
    if namespace is not None:
        namespace = namespace[1:-1]
    if namespace == "":
        namespace = None
    return namespace, local_name


def write_hierarchy(xml_elt):
    ancest = xml_elt.xpath("ancestor-or-self::*")
    hierarchy = ""
    for idx, elt in enumerate(ancest):
        hierarchy += f"/{elt.xpath('name()')}"
        if elt.get("id"):
            hierarchy += f'[id="{elt.get("id")}"]'
        elif idx != 0:
            xpath_expr = f"count(../{elt.xpath('name()')})"
            max_index = int(elt.xpath(xpath_expr, namespaces=NS))
            if max_index > 1:
                xpath_expr = f"count(preceding-sibling::{elt.xpath('name()')})+1"
                elt_index = int(elt.xpath(xpath_expr, namespaces=NS))
                hierarchy += f"[{elt_index}]"
    return hierarchy


def log_element(xml_elt, attributes=None, text_content=False, msg=""):
    log_entry = write_hierarchy(xml_elt)
    if msg:
        log_entry += "\n    " + msg
    if attributes:
        log_entry += "\n   "
        for attrname in attributes:
            attrval = xml_elt.xpath(f"string(@{attrname})", namespaces=NS)
            if len(attrval) == 0:
                continue
            if len(attrval) > 50:
                attrval = attrval[:47] + "..."
            log_entry += f' {attrname}="{attrval}"'
    if text_content:
        log_entry += "\n    Text content: "
        txt = xml_elt.xpath("string()")
        if len(txt) > 50:
            txt = txt[:47] + "..."
        log_entry += txt
    return log_entry


def suppress_element(xml_elt):
    parent = xml_elt.getparent()
    text = (xml_elt.text or "") + (xml_elt.tail or "")
    previous = xml_elt.getprevious()
    if previous is not None:
        previous.tail = (previous.tail or "") + text
    else:
        parent.text = (parent.text or "") + text
    parent.remove(xml_elt)


def add_text_around_element(xml_elt, before="", after=""):
    previous = xml_elt.getprevious()
    parent = xml_elt.getparent()
    if before:
        if previous is not None:
            previous.tail = (previous.tail or "") + before
        else:
            parent.text = (parent.text or "") + before
    if after:
        xml_elt.tail = (xml_elt.tail or "") + after


def adjust_content_in_mixed(xml_elt, keep_tags=tuple()):
    """
    Erase from ``xml_elt`` all the XML elements except those whose tag name
    is given in ``keep_tags`` tuple. The text inside ``xml_elt`` and its
    children is kept (even if the elements are removed).

    If an XML element must be kept, it is kept as it is (with all its
    sub-elements). Therefore, if you want to erase XML elements that can
    occur at several levels in the XML tree, you have to walk depth-first in
    the tree and call the function first from the bottom levels and upwards.
    """
    for child in xml_elt:
        if child.tag in keep_tags:
            # If child must be kept, keep it as it is and go to next child
            continue
        # Recursively call the same function to get all the text content from
        # child (``keep_tags`` is empty because we don't want to keep any
        # XML element from ``child`` that will not be kept).
        adjust_content_in_mixed(child, tuple())
        # Keep text content of ``child`` inside the element before ``child``
        child_text_content = (child.text or "") + (child.tail or "")
        if child_text_content:
            previous = child.getprevious()
            if previous is not None:
                previous.tail = (previous.tail or "") + child_text_content
            else:
                xml_elt.text = (xml_elt.text or "") + child_text_content
        # Finally, remove child from the XML tree
        xml_elt.remove(child)


def insert_child_at_element_beginning(xml_elt, child):
    if xml_elt.text is not None:
        child.tail = (child.tail or "") + xml_elt.text
        xml_elt.text = None
    xml_elt.insert(0, child)


def insert_text_at_element_end(xml_elt, text):
    if not text:
        return
    if len(xml_elt) == 0:
        xml_elt.text = (xml_elt.text or "") + text
    else:
        last_child = xml_elt[-1]
        last_child.tail = (last_child.tail or "") + text


def insert_text_before_element(xml_elt, text):
    if not text:
        return
    prev = xml_elt.getprevious()
    if prev is None:
        parent = xml_elt.get_parent()
        parent.text = (parent.text or "") + text
    else:
        prev.tail = (prev.tail or "") + text
