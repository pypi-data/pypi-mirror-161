# -*- coding: utf-8 -*-
"""
Module defining two global libraries that contains all the known formats
and the known actions.

The :func:`~glamconv.transformer.libraries.register_action` and
:func:`~glamconv.transformer.libraries.register_format` functions can
be used to register an action class or a format inside these libraries. The
:func:`~glamconv.transformer.libraries.get_action` and
:func:`~glamconv.transformer.libraries.get_format` functions can be used
to retrieve an action class or a format from these libraries. A format is
registred with its unique identifier (``uid``), an action is registred with
the identifier of the format it applies to and its name (if the action can be
applied to multiple formats, it is registred multiple times).
"""

import operator
from glamconv.transformer.actions import AbstractAction
from glamconv.transformer.formats import DataFormat


ACTIONS_LIBRARY = {}  # {format_uid: {action_uid: AbstractAction, }, }
FORMATS_LIBRARY = {}  # {format_uid: DataFormat(), }


# Actions


def register_action(action_class, format_uid=None):
    assert issubclass(action_class, AbstractAction)
    if format_uid is not None:
        if format_uid not in ACTIONS_LIBRARY:
            ACTIONS_LIBRARY[format_uid] = {}
        ACTIONS_LIBRARY[format_uid][action_class.uid] = action_class
    else:
        for frmt in action_class.applicable_for:
            if format_uid not in ACTIONS_LIBRARY:
                ACTIONS_LIBRARY[format_uid] = {}
            ACTIONS_LIBRARY[format_uid][action_class.uid] = action_class


def get_action(format_uid, action_uid):
    return ACTIONS_LIBRARY[format_uid][action_uid]


def list_action_categories(format_uid, family=None):
    sel_actions = ACTIONS_LIBRARY.get(format_uid, {}).values()
    if family is not None:
        sel_actions = [act for act in sel_actions if act.family == family]
    return sorted(set([act.category for act in sel_actions]))


def list_actions(format_uid, family=None, category=None):
    sel_actions = ACTIONS_LIBRARY.get(format_uid, {}).values()
    if family is not None:
        sel_actions = [act for act in sel_actions if act.family == family]
    if category is not None:
        sel_actions = [act for act in sel_actions if act.category == category]
    return sorted(sel_actions, key=operator.attrgetter("name"))


# Formats
def register_format(data_format):
    assert isinstance(data_format, DataFormat)
    FORMATS_LIBRARY[data_format.uid] = data_format
    register_action(data_format.reading_class, data_format.uid)
    register_action(data_format.writing_class, data_format.uid)
    register_action(data_format.validating_class, data_format.uid)


def get_format(format_uid):
    return FORMATS_LIBRARY[format_uid]


def list_formats():
    return sorted(FORMATS_LIBRARY.values(), key=operator.attrgetter("name"))
