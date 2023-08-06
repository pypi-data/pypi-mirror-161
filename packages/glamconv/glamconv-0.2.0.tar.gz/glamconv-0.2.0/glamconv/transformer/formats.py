# -*- coding: utf-8 -*-
"""
Module defining a data format.

A data format has a name, a MIME content-type and is associated
with a reading action for retrieving the data from a file in this
format, a writing action for the opposite purpose and a validating
action to check the data is valid (after reading or before writing).
"""


class DataFormat(object):
    def __init__(self, uid, name, content_type, file_extension, desc):
        self.uid = uid
        self.name = name
        self.content_type = content_type
        self.file_ext = file_extension  # with leading "."
        self.desc = desc
        self.reading_class = None  # ReadAction
        self.writing_class = None  # WriteAction
        self.validating_class = None  # ValidateAction

    def dump(self):
        data = {}
        data["formatUid"] = self.uid
        data["name"] = self.name
        data["desc"] = self.desc
        data["contentType"] = self.content_type
        data["fileExtension"] = self.file_ext
        return data
