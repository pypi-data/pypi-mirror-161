# -*- coding: utf-8 -*-
"""
Module containing actions for changing the values of the vocabulary-controlled
attributes in order to have a legit value.
"""

import re
from glamconv.ead.utils import log_element, add_text_around_element
from glamconv.ead.formats import EAD_2002
from glamconv.transformer.actions import TransformAction


OTHLEV_REGEXP = re.compile(r"^([A-Za-z]|:|_)([0-9A-Za-z]|:|_|-|\.)*$")


class ArchdescLevelAttribAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "archdesc-level-adjuster"
    name = "Adjusting the value of level attribute in <archdesc>"
    category = "Cleansing"
    desc = (
        "In the 'level' attribute of <archdesc> elements the only "
        "possible legit value is \"fonds\". This action sets 'level' "
        "to its legit value and puts its previous value in the "
        "'otherlevel' attribute of <archsdesc> if it is empty."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for arch in xml_root.xpath('.//archdesc[not(@level) or @level!="fonds"]'):
            msg = ""
            value = arch.get("level", "")
            if (
                value not in ["", "otherlevel"]
                and arch.get("otherlevel", "") != ""
                and OTHLEV_REGEXP.match(value) is not None
            ):
                arch.set("otherlevel", value)
            else:
                msg = f"    Old value: {value}"
            arch.set("level", "fonds")
            count += 1
            if log_details:
                log_data.append(log_element(arch, msg=msg))
        if count > 0:
            logger.warning(
                "The 'level' attribute in the <archdesc> element can only "
                f'have one value: "fonds". {count:d} elements have been '
                "corrected."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class DscTypeAttribAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "dsc-type-adjuster"
    name = "Adjusting the value of type attribute in <dsc>"
    category = "Cleansing"
    desc = (
        "In the 'type' attribute of <dsc> elements the only possible "
        "legit value is \"othertype\". This action sets 'type' "
        "to its legit value."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for dsc in xml_root.xpath('.//dsc[@type!="othertype"]'):
            if log_details:
                msg = f"    Old value: {dsc.get('type')}"
                log_data.append(log_element(dsc, msg=msg))
            dsc.attrib["type"] = "othertype"
            count += 1
        if count > 0:
            logger.warning(
                "The 'type' attribute in the <dsc> element can only have "
                f'one value: "othertype". {count:d} elements have been '
                "corrected."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


class EmphRenderAttribAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "emph-render-adjuster"
    name = "Adjusting the value of render attribute in <emph>"
    category = "Cleansing"
    desc = (
        "In the 'render' attribute of <emph> elements the only possible "
        'legit values are "bold" and "italic". If the value contains '
        '"bold", sets the value to "bold", else if the value '
        'contains "italic", sets the value to "italic", else deletes '
        "the value. If the value contains the mention of quotes (single "
        "or double), adds them to the text before and after the <emph> "
        "element."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for emph in xml_root.xpath('.//emph[@render!="bold" and @render!="italic"]'):
            value = emph.attrib.pop("render", "")
            if value == "":
                continue
            if "bold" in value:
                emph.set("render", "bold")
            elif "italic" in value:
                emph.set("render", "italic")
            if "doublequote" in value:
                add_text_around_element(emph, "« ", " »")
            elif "singlequote" in value:
                add_text_around_element(emph, "\u2018", "\u2019")
            if log_details:
                msg = f"    Old value: {value}"
                log_data.append(log_element(emph, msg=msg, text_content=True))
            count += 1
        if count > 0:
            logger.warning(
                "The render attribute in the <emph> element can only have "
                f'the values "bold" or "italic". {count:d} elements have been '
                "corrected."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


LNGS = (
    "roh sco scn rom ron alg oss ale alb scc mni nld mno osa mnc scr oci "
    "mwr crp lua jav hrv lub lun twi aus roa ven uga mwl ger mga hit fas "
    "ssw lug luo fat fan fao lui tgl ita geo him hin mlg din mun hye gba "
    "guj cmc slk bad nep iba ban ady div bam bak shn bai arp tel tem arw "
    "nwc ara tkl arc nbl ter sel tet arm arn ave lus mus sun kut suk kur "
    "wol kum sus iro new oji kua sux mlt iku hai tup tur men tut mic grc "
    "tuk tum mul lez nav cop cos cor gla bos gwi gle eka glg akk und dra "
    "aka tlh bod glv jrb vie ipk por uzb pon pol sah sgn sga tgk bre apa "
    "wak bra aym cha chb che fre chg swa chi chk fro chm chn cho chp cpf "
    "chr xal chu chv chy fry dut hat msa gay oto ota hmn hmo ice niu myv "
    "iii gaa fur ndo ibo ina car slv xho deu cau cat cai slo del fil den "
    "ilo inh ful sla cad tat jpn vol myn vot ind dzo spa tam jpr tah tai "
    "bis cze pap afh pau eng afa ewe csb phi paa nyn nyo nym bnt nya sio "
    "sin afr map mas mar lah phn sna may kir yao snk dgr syr mac mad mag "
    "mai mah lav mal mao man egy pag znd sit gmh epo jbo tiv tha dum fon "
    "zen kbd enm kha sam tsn tso dsb cus ell fiu ssa wen wel byn elx gem "
    "uig ada fij tli fin hau eus haw bin amh non ceb bih mos dan nog bat "
    "nob dak moh ces mon dar mol son day nor bas cel pal baq pam hil kpe "
    "dua sot lad lam mdf snd tvl lao abk mdr ijo gon goh sms per smo smn "
    "peo smj smi pan tmh got sme bla sma gor hsb nic nia run ast mkd sag "
    "cre fra bik orm que ori rus crh asm pus kik gez srd ltz ach nde sqi "
    "ath kru srr ido srp nub kro wln isl ava krc nds zun zul kin umb sog "
    "nso swe som yap lat frm art mak zap yid kok vai kom her kon ukr lol "
    "mkh ton heb loz kos kor was tog ira pli sid bur hun hup bul wal bua "
    "bug cym udm bej gil ben bel bem tsi aze war zha ace rum aar ber nzi "
    "zho nno sai ang pra san bho sal pro arg raj sad khi rar khm rap kho "
    "sas ine sem sat min lim lin nai tir nah lit efi nap gre grb btk nau "
    "grn ypk mis tig yor tib kac kab kaa ile kan kam kal kas kar mya est "
    "kaw kau kat kaz tyv awa kmb urd doi ewo cpe tpi mri dyu cpp bal inc"
)
LNGS = tuple(LNGS.split(" "))


class LanguageLangcodeAttribAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "language-langcode-adjuster"
    name = "Adjusting the value of langcode attribute in <language>"
    category = "Cleansing"
    desc = (
        "The 'langcode' attribute of <language> elements can only take "
        "a definite set of values. This action erases the attributes that "
        "don't have a legit value."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//language[@langcode]"):
            value = elt.attrib.pop("langcode", "").lower()
            if value in LNGS:
                elt.set("langcode", value)
            else:
                if log_details:
                    msg = f"    Deleted value: {value}"
                    log_data.append(log_element(elt, msg=msg))
                count += 1
        if count > 0:
            logger.warning(
                "The 'langcode' attribute in the <language> element can only "
                f"have a value taken from a fixed vocabulary. {count:d} "
                "elements have had their 'langcode' attribute deleted because "
                "of a non-legit value."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root


SCRS = (
    "Tfng Shaw Cirt Guru Hebr Geor Zzzz Phnx Hrkt Plrd Ogam Telu Bopo "
    "Dsrt Xsux Visp Hmng Hano Bali Gujr Hang Thaa Sinh Hans Hant Talu "
    "Mong Deva Sara Qabx Tagb Inds Xpeo Geok Tale Mymr Mand Perm Bugi "
    "Phag Brai Brah Mlym Tibt Kali Batk Vaii Sylo Lina Teng Mero Limb "
    "Kana Yiii Roro Java Taml Orya Laoo Ugar Cyrl Nkoo Armn Cyrs Latg "
    "Latf Khmr Khar Egyh Latn Maya Ethi Goth Ital Arab Zxxx Buhd Copt "
    "Thai Cprt Linb Lepc Osma Runr Glag Hira Syre Hani Orkh Hung Grek "
    "Qaaa Egyd Cher Zyyy Cham Syrc Blis Cans Beng Egyp Syrj Tglg Syrn "
    "Knda"
)
SCRS = tuple(SCRS.split(" "))


class LanguageScriptcodeAttribAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "language-scriptcode-adjuster"
    name = "Adjusting the value of scriptcode attribute in <language>"
    category = "Cleansing"
    desc = (
        "The 'scriptcode' attribute of <language> elements can only take "
        "a definite set of values. This action erases the attributes that "
        "don't have a legit value."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for elt in xml_root.xpath(".//language[@scriptcode]"):
            value = elt.attrib.pop("scriptcode", "").capitalize()
            if value in SCRS:
                elt.set("scriptcode", value)
            else:
                if log_details:
                    msg = f"    Deleted value: {value}"
                    log_data.append(log_element(elt, msg=msg))
                count += 1
        if count > 0:
            logger.warning(
                "The 'scriptcode' attribute in the <language> element can "
                f"only have a value taken from a fixed vocabulary. {count:d} "
                "elements have had their 'scriptcode' attribute deleted "
                "because of a non-legit value."
            )
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        # Return the cleaned EAD tree
        return xml_root


class ListAttribsAdjuster(TransformAction):
    applicable_for = (EAD_2002,)
    uid = "list-attribs-adjuster"
    name = "Adjusting the value of attributes in <list>"
    category = "Cleansing"
    desc = (
        "The 'numeration' and the 'type' attributes of <list> elements "
        "can only have a few legit value. This action erases the "
        "attributes whose value is not legit."
    )

    def _execute(self, xml_root, logger, log_details):
        count = 0
        if log_details:
            log_data = []
        for list_elt in xml_root.xpath(".//list[@numeration or @type]"):
            msg = ""
            if list_elt.get("numeration") not in [None, "arabic"]:
                val = list_elt.attrib.pop("numeration")
                msg += f' numeration="{val}"'
            if list_elt.get("type") not in [None, "ordered", "marked"]:
                val = list_elt.attrib.pop("type")
                msg += f' type="{val}"'
            if msg != "":
                if log_details:
                    log_data.append(
                        log_element(list_elt, msg=("    Deleted attributes:" + msg))
                    )
                count += 1
        if count > 0:
            logger.warning(
                "The attributes of <list> elements can only have specific "
                f"values. {count:d} elements have had their attributes deleted "
                "because of a non-legit value:"
            ),
            if log_details:
                logger.warning(
                    "The following elements have been corrected:\n"
                    + "\n".join(log_data)
                )
        return xml_root
