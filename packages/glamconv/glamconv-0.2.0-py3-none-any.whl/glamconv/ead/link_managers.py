# -*- coding: utf-8 -*-
"""
Module containing actions for processing the links (URLs and internal links)
inside the XML elements.
"""

from urllib.parse import urlencode

from lxml import etree

from glamconv.ead.utils import NS, split_qname, log_element
from glamconv.ead.formats import EAD_2002, EAD_APE
from glamconv.transformer.actions import TransformAction
from glamconv.transformer.parameters import SingleParameter, CouplesParameter


class InternalLinkTransformer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "internal-link-transformer"
    name = "Transforming <ref> and <ptr> into <extref> and <extptr>"
    category = "Links & Refs"
    desc = (
        "In Ape-EAD, the elements describing an internal link (<ptr> and "
        "<ref>) doesn't exist anymore. This action transforms the <ref> "
        "elements into <extref> elements and the <ptr> elements into "
        "<extptr> elements. The URL of the new link will have the "
        'following form: "#internal-id".'
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//ref|.//ptr"):
            _, name = split_qname(elt.tag)
            elt.tag = f"ext{name}"
            if "target" in elt.attrib:
                elt.set("href", f"#{elt.attrib.pop('target')}")
            count += 1
            if log_details:
                log_data.append(log_element(elt, attributes=("href", "xlink:href")))
        if count > 0:
            logger.warning(
                "Transforming elements containing an internal link into "
                f"elements containing an external link. {count:d} elements "
                "have been modified."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root


class ExternalLinkTransformer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "external-link-transformer"
    name = "Transforming <archref>, <bibref>, <extptr>, <extref>"
    category = "Links & Refs"
    desc = (
        "This action transforms the <archref>, <bibref>, <extptr> and "
        "<extref> elements into the legit element for describing the "
        "external link in the current parent element (e.g. <bibref> in "
        "<bibliography>, <extref> in <p>)."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        names = (
            "archref",
            "bibref",
            "extptr",
            "extref",
        )
        legit_elt = {
            "bibliography": "bibref",
            "unitid": "extptr",
            "descrules": "extref",
            "item": "extref",
            "p": "extref",
            "repository": "extref",
        }
        xpath_req = " | ".join(f".//{eltname}" for eltname in names)
        for elt in xml_root.xpath(xpath_req):
            parent = elt.getparent()
            newname = legit_elt.get(split_qname(parent.tag)[1], None)
            if newname is None:
                continue
            _, oldname = split_qname(elt.tag)
            if newname == oldname:
                continue
            elt.tag = newname
            count += 1
            lnk = elt.get("href") or elt.get(f"{{{NS['xlink']}}}href", "")
            if newname == "extptr" and len(elt.text or "") > 0:
                if log_details:
                    log_data.append(
                        log_element(
                            elt,
                            msg="    Text content will be deleted",
                            attributes=("href", "xlink:href"),
                            text_content=True,
                        )
                    )
                elt.text = None
            elif oldname == "extptr" and len(lnk) > 0:
                elt.text = lnk
                if log_details:
                    log_data.append(
                        log_element(
                            elt,
                            msg="    href will be added as text content",
                            attributes=("href", "xlink:href"),
                        )
                    )
            elif log_details:
                log_data.append(
                    log_element(
                        elt, attributes=("href", "xlink:href"), text_content=True
                    )
                )
        if count > 0:
            logger.warning(
                "Transforming external link elements into the element that "
                f"can occur inside the parent element. {count:d} elements have "
                "been modified."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root


class DaodescEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "daodesc-eraser"
    name = "Deleting <daodesc> from <dao> and <daogrp>"
    category = "Links & Refs"
    desc = (
        "<daodesc> elements don't exist anymore in Ape-EAD. This "
        "action deletes the <daodesc> that were defined in <dao> or "
        "<daogrp> elements."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//daodesc"):
            if log_details:
                log_data.append(log_element(elt, text_content=True))
            elt.getparent().remove(elt)
            count += 1
        if count > 0:
            logger.warning(f"{count:d} <daodesc> elements have been deleted.")
            if log_details:
                logger.warning(
                    "The following elements have been deleted:\n" + "\n".join(log_data)
                )
        return xml_root


class DaoContentEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "dao-content-eraser"
    name = "Deleting content in <dao>"
    category = "Links & Refs"
    desc = (
        "In Ape-EAD, <dao> elements must be empty (no text, not even "
        "spaces). This action deletes the content that might remain in "
        "<dao> elements."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath('.//dao[text() != "" or node()]'):
            elt.text = None
            for child in elt:
                elt.remove(child)
            count += 1
            if log_details:
                log_data.append(log_element(elt, attributes=("href", "xlink:href")))
        if count > 0:
            logger.warning(
                f"Inner content has been deleted from {count:d} <dao> elements."
            )
            if log_details:
                logger.warning(
                    "The following <dao> elements have been emptied:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class DaogrpTransformer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "daogrp-transformer"
    name = "Transforming <daogrp> into <dao>"
    category = "Links & Refs"
    desc = (
        "Ape-EAD doesn't have any element for describing the extended "
        "links and their various parts (locator, arc, resource). The "
        "only possible links are simple links. Instead of simply "
        "deleting the <daogrp> elements, this action retrieves the "
        "<daoloc> that often describe some resources (images, etc.) "
        "and transforms them into <dao> elements outside the <daogrp>. "
        "The other elements in the <daogrp> (resources, arcs, etc.) are "
        "deleted."
    )

    def _execute(self, xml_root, logger, log_details):
        count1, count2 = 0, 0
        if log_details:
            log_data1 = []
            log_data2 = []
        for daogrp in xml_root.xpath(".//daogrp"):
            for daoloc in daogrp.xpath("daoloc"):
                daoloc.tag = "dao"
                label = daoloc.attrib.pop("label", "").strip()
                if label != "" and "role" not in daoloc.attrib:
                    daoloc.set("role", label)
                daogrp.addprevious(daoloc)
                count1 += 1
                if log_details:
                    log_data1.append(
                        log_element(daoloc, attributes=("href", "xlink:href"))
                    )
            if len(daogrp) > 0:
                count2 += 1
                if log_details:
                    log_data2.append(log_element(daogrp))
            daogrp.getparent().remove(daogrp)
        if count1 > 0:
            logger.warning(
                f"{count1:d} <dao> elements have been defined from <daoloc> "
                "found in <daogrp> elements."
            )
            if log_details:
                logger.warning(
                    "The following <dao> elements have been defined:\n"
                    + "\n".join(log_data1)
                )
        if count2 > 0:
            logger.warning(
                f"{count2:d} <daogrp> elements that contained data other "
                "than <daoloc> have been deleted."
            )
            if log_details:
                logger.warning(
                    "The following non-empty <daogrp> elements have been deleted:\n"
                    + "\n".join(log_data2)
                )
        return xml_root


class ArchdescCDaoMover(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "archdesc-c-dao-mover"
    name = "Moving <dao> inside <c> or <archdesc> into <did>"
    category = "Links & Refs"
    desc = (
        "In Ape-EAD, the <dao> elements can't be directly inserted into "
        "a <c> or an <archdesc> element. This action moves the <dao> "
        "elements from these <c> or <archdesc> into the <did> child "
        "element they always contain."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for dao in xml_root.xpath(".//c/dao | .//archdesc/dao"):
            dids = dao.xpath("../did")
            if len(dids) == 0:
                continue
            did = dids[0]
            did.append(dao)
            count += 1
            if log_details:
                log_data.append(log_element(dao, attributes=("href", "xlink:href")))
        if count > 0:
            logger.warning(
                f"{count:d} <dao> elements have been moved from a <c> or an "
                "<archdesc> into their <did> sibling."
            )
            if log_details:
                logger.warning(
                    "The following <dao> elements have been moved:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class OddDaoTransformer(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "odd-dao-transformer"
    name = "Transforming <dao> inside <odd>"
    category = "Links & Refs"
    desc = (
        "In Ape-EAD, the <dao> elements can't exist inside an <odd> "
        "element. This action transforms these <dao> elements into "
        "<extref> elements inside a <list>."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for odd in xml_root.xpath(".//odd[dao]"):
            lst_elt = etree.SubElement(odd, "list")
            for dao in odd.xpath("dao"):
                dao.tag = "extref"
                lnk = dao.get("href") or dao.get(f"{{{NS['xlink']}}}href", "")
                title = dao.get("title") or dao.get(f"{{{NS['xlink']}}}title", "")
                if title != "":
                    dao.text = title
                else:
                    dao.text = lnk
                itm = etree.SubElement(lst_elt, "item")
                itm.append(dao)
                count += 1
                if log_details:
                    log_data.append(log_element(dao, attributes=("href", "xlink:href")))
        if count > 0:
            logger.warning(
                f"{count:d} <dao> elements inside an <odd> have been "
                "transformed in <extref> element."
            )
            if log_details:
                logger.warning(
                    "Non-legit <dao> elements have been transformed into the "
                    "following elements:\n" + "\n".join(log_data),
                )
        return xml_root


class LinkgrpEraser(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "linkgrp-eraser"
    name = "Erasing the <linkgrp>"
    category = "Links & Refs"
    desc = (
        "Ape-EAD doesn't have any element for describing the extended "
        "links and their various parts (locator, arc, resource). The "
        "only possible links are simple links. This action deletes the "
        "<linkgrp> elements that describe an extended link."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//linkgrp"):
            if log_details:
                log_data.append(log_element(elt))
            elt.getparent().remove(elt)
            count += 1
        if count > 0:
            logger.warning(f"{count:d} <linkgrp> elements have been deleted.")
            if log_details:
                logger.warning(
                    "The following elements have been deleted:\n" + "\n".join(log_data)
                )
        return xml_root


class XLinkAttribSetter(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "xlink-setter"
    name = "Using xlink attributes in links"
    category = "Links & Refs"
    desc = (
        "This action transforms the attributes of <bibref>, <extprt>, "
        "<extref> and <dao> elements that describe the links into the "
        "corresponding xlink attributes."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        names = (
            "bibref",
            "extptr",
            "extref",
            "dao",
        )
        xpath_req = " | ".join(f".//{eltname}" for eltname in names)
        attrs = ("actuate", "arcrole", "href", "role", "show", "title")
        actuate_conv = {
            "onload": "onLoad",
            "onrequest": "onRequest",
            "actuatenone": "none",
            "actuateother": "other",
        }
        show_conv = {
            "new": "new",
            "embed": "embed",
            "showother": "other",
            "shownone": "none",
            "replace": "replace",
        }
        for elt in xml_root.xpath(xpath_req):
            # Link is always a simple link in Ape-EAD
            elt.attrib.pop("type", None)
            elt.set(f"{{{NS['xlink']}}}type", "simple")
            # Set xlink attributes
            num = 0
            for attname in elt.attrib:
                namespace, name = split_qname(attname)
                if namespace == NS["xlink"] or name not in attrs:
                    continue
                num = 1
                xlink_name = f"{{{NS['xlink']}}}{name}"
                # Delete attribute but keep its value
                attvalue = elt.attrib.pop(attname)
                if namespace != NS["xlink"] and xlink_name in elt.attrib:
                    # If already have a xlink attribute with the same local
                    # name, keep this xlink attribute and forget the current
                    # one
                    continue
                if name == "actuate":
                    attvalue = actuate_conv.get(attvalue)
                elif name == "show":
                    attvalue = show_conv.get(attvalue)
                if attvalue is not None:
                    elt.set(xlink_name, attvalue)
            count += num
            if log_details and num > 0:
                log_data.append(log_element(elt, attributes=("xlink:href",)))
        if count > 0:
            logger.warning(
                f"{count:d} elements describing a link have had their "
                "attributes transformed into xlink attributes."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root


class DaoCharacterReplacer(TransformAction):
    applicable_for = (EAD_2002, EAD_APE)
    uid = "dao-character-replacer"
    name = "Replacing characters in the <dao> links"
    category = "Links & Refs"
    desc = (
        "This action replaces an expression with another one inside the "
        "resource link (xlink:href) defined in the <dao> elements. Please "
        "be sure to execute this action after the link attributes have "
        "been transformed in xlink attributes."
    )
    params_def = (
        SingleParameter(
            "old",
            "Old",
            "Expression to be found in the link and to be replaced by the new one",
            "Text",
            str,
            "",
        ),
        SingleParameter(
            "new",
            "New",
            "Expression replacing the old one in the link",
            "Text",
            str,
            "",
        ),
    )

    def _execute(self, xml_root, logger, log_details, old, new):
        count = 0
        if log_details:
            log_data = []
        for dao in xml_root.xpath(".//dao"):
            old_href = dao.get(f"{{{NS['xlink']}}}href")
            if old in old_href:
                new_href = old_href.replace(old, new)
                dao.set(f"{{{NS['xlink']}}}href", new_href)
                count += 1
                if log_details:
                    msg = f"    Old href: {old_href}\n    New href: {new_href}"
                    log_data.append(log_element(dao, msg=msg))
        if count > 0:
            logger.warning(
                f"{count:d} <dao> elements have had their 'xlink:href' "
                "attribute modified."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root


class DaoAbsoluteUrlBuilder(TransformAction):
    applicable_for = (EAD_2002, EAD_APE)
    uid = "dao-absolute-url-builder"
    name = "Building absolute URLs in the <dao> links"
    category = "Links & Refs"
    desc = (
        "Builds an absolute URL from the data found inside the xlink:href "
        "attribute of the <dao> elements. The URL contains an address "
        "(e.g. http://www.exemple.com/data/{href}) and parameters "
        "defined as key/value couples (e.g. height: 128, width: 128, "
        "id: {href}). In one of the other, the {href} expression can "
        "be used to insert the content of the href attribute of the "
        "<dao> element (cf. previous examples). Please be sure to execute "
        "this action after the link attributes have been transformed in "
        "xlink attributes."
    )
    params_def = (
        SingleParameter(
            "url_address",
            "Address",
            "URL address. The expression {href} can be used to insert the "
            "content of the href attribute of the <dao> element.",
            "Text",
            str,
            "",
        ),
        CouplesParameter(
            "url_params",
            "Parameters",
            "URL parameters defined as a sequence of couples key/value. In "
            "these values, the expression {href} can be used to insert the "
            "content of the href attribute of the <dao> element.",
            "List of couples (text, text)",
            str,
            str,
            [],
        ),
    )

    def _execute(self, xml_root, logger, log_details, url_address, url_params):
        count = 0
        if log_details:
            log_data = []
        for dao in xml_root.xpath(".//dao"):
            old_href = dao.get(f"{{{NS['xlink']}}}href")
            if "{href}" in url_address:
                new_href = url_address.format(href=old_href)
            else:
                new_href = url_address
            params = []
            for key, value in url_params:
                if "{href}" in value:
                    params.append((key, value.format(href=old_href)))
                else:
                    params.append((key, value))
            if len(params) > 0:
                new_href += f"?{urlencode(params)}"
            dao.set(f"{{{NS['xlink']}}}href", new_href)
            count += 1
            if log_details:
                msg = f"    Old href: {old_href}\n    New href: {new_href}"
                log_data.append(log_element(dao, msg=msg))
        if count > 0:
            logger.warning(
                f"{count:d} <dao> elements have had an absolute URL built "
                "in their 'xlink:href' attribute."
            )
            if log_details:
                logger.warning(
                    "The following elements have been modified:\n" + "\n".join(log_data)
                )
        return xml_root
