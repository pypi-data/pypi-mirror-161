# -*- coding: utf-8 -*-
"""
Module defining a generic action and basic actions.

Actions will be run one after another into a process. Actions have a
family (read / write / validate / transform), a category and a
name. Each action takes an input object, modifies it and returns an
output object. For the read actions, the input object is a file object
(form which a stream of bytes can be read). For the write actions, the
output object is a stream of bytes that can be directly written into a
file object. An action can have parameters that are defined as
:class:`~glamconv.transformer.parameters.AbstractParameter`
objects. The values of the parameters are given when running the
action.

Some actions can be applied to a data format, others to another
one. Therefore, each action has a list of the formats they can be
applied to.
"""


READ_ACTION = "read-action"
"""
Family of the actions that read a file and build an object that can be passed
from one action to another (e.g. an XML tree).

Type: :class:`str`
"""
WRITE_ACTION = "write-action"
"""
Family of the actions that write a file from an object passed from one action
to another (e.g. an XML tree).

Type: :class:`str`
"""
VALIDATE_ACTION = "validate-action"
"""
Family of the actions that validate an object passed from one action to
another (e.g. an XML tree) in order to verify it meets all the constraints
of the associated format (e.g. constraints described in a DTD or an XML
Schema).

Type: :class:`str`
"""
TRANSFORM_ACTION = "transform-action"
"""
Family of the actions that transform an object passed from one action to
another (e.g. an XML tree).

Type: :class:`str`
"""


class AbstractAction(object):
    family = None
    uid = None
    name = ""
    category = ""
    desc = ""
    applicable_for = set()  # (DataFormat, )
    params_def = tuple()  # (AbstractParameter, )

    @classmethod
    def dump(cls):
        return {
            "uid": cls.uid,
            "name": cls.name,
            "category": cls.category,
            "desc": cls.desc,
            "applicableFor": sorted(frmt.uid for frmt in cls.applicable_for),
            "paramsDesc": sorted(pdef.dump() for pdef in cls.params_def),
        }

    def __init__(self):
        if self.__class__ is AbstractAction:
            raise NotImplementedError("Abstract class can't be instantiated")

    def build_params_val(self, specif_params, logger):
        if specif_params is None:
            specif_params = {}
        values = {}
        for pdef in self.params_def:
            try:
                values[pdef.uid] = pdef.build_value(specif_params.get(pdef.uid))
            except ValueError:
                logger.error(
                    f"Type of {repr(pdef.name)} parameter should be "
                    f"{pdef.type_desc}. Can't convert the value:\n"
                    f"{repr(specif_params.get(pdef.uid))}"
                )
                values[pdef.uid] = pdef.build_value(None)  # Default value
        return values

    def log_start(self, logger, param_values):
        log_values = []
        for pdef in self.params_def:
            log_values.append(pdef.log_value(param_values[pdef.uid]))
        logger.action_start(self.name, log_values)

    def run(self, input_obj, logger, log_details, specif_params):
        values = self.build_params_val(specif_params, logger)
        self.log_start(logger, values)
        output_obj = self._execute(input_obj, logger, log_details, **values)
        return output_obj

    def _execute(self, input_obj, logger, log_details, **kwargs):
        # To be written in the sub-classes
        raise NotImplementedError("Can't call an abstract method")


class TransformAction(AbstractAction):
    family = TRANSFORM_ACTION
    uid = "no-operation"
    name = "No transformation"
    category = ""
    desc = (
        "This action doesn't make any transformation and returns the "
        "input object as if."
    )
    params_def = tuple()  # (AbstractParameter, )

    def _execute(self, input_obj, logger, log_details, **kwargs):
        # To be changed in the sub-classes
        return input_obj


class ValidateAction(AbstractAction):
    family = VALIDATE_ACTION
    uid = "no-validation"
    name = "Always validating"
    category = "Validation"
    desc = (
        "This action validates an object previously read by a reading "
        "action. In this basic action, the validation always returns true."
    )
    params_def = tuple()  # (AbstractParameter, )

    def _execute(self, input_flow, logger, log_details, **kwargs):
        # To be written in the sub-classes
        return True


class ReadAction(AbstractAction):
    family = READ_ACTION
    uid = "binary-reading"
    name = "Reading a binary string from an input file"
    category = "Reading"
    desc = (
        "This action reads an opened file and returns its content " "as a bytes string."
    )
    params_def = tuple()  # (AbstractParameter, )

    def _execute(self, input_flow, logger, log_details, **kwargs):
        # To be changed in the sub-classes
        input_obj = input_flow.read()
        return input_obj


class WriteAction(AbstractAction):
    family = WRITE_ACTION
    uid = "binary-writing"
    name = "Writing a binary string into an output file"
    category = "Writing"
    desc = (
        "This action returns the data from a binary so that it can be "
        "written into a file."
    )
    params_def = tuple()  # (AbstractParameter, )

    def _execute(self, input_obj, logger, log_details, **kwargs):
        # To be changed in the sub-classes
        return input_obj
