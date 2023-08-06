# -*- coding: utf-8 -*-
"""
Module defining the classes used to log the run of a transformation process
in order to transform of a file into another file thanks to a series of steps
(action + parameter values).
"""

import datetime as dtm
import logging


ERROR = "error"
"""
Type of log message describing an error

Type: :class:`str`
"""
WARNING = "warning"
"""
Type of log message describing an error

Type: :class:`str`
"""
INFO = "info"
"""
Type of log message describing an error

Type: :class:`str`
"""


class RunLog(object):
    def __init__(self, stdlogger=None):
        self.start_timestamp = None
        self.steps_log = []  # StepLog
        self.end_timestamp = None
        self.input_validation = None
        self.input_validation_message = ""
        self.output_validation = None
        self.output_validation_message = ""
        self.failure = False
        self.failure_step_index = None
        self.failure_message = ""
        self._current_log = None
        self.stdlogger = stdlogger or logging.getLogger("glamconv.transform")

    @property
    def result(self):
        if self.failure:
            return False
        if self.output_validation is not None:
            return self.output_validation
        # output_validation can still be None if there was only two steps
        # for validating a file
        return self.input_validation or False

    def start_run(self):
        self.start_timestamp = dtm.datetime.utcnow()

    def end_run(self):
        self.end_timestamp = dtm.datetime.utcnow()

    def start_step(self, index):
        self._current_step_log = StepLog(index)
        self.steps_log.append(self._current_step_log)

    def end_step(self):
        self._current_step_log = None

    def action_start(self, name, param_values):
        if self._current_step_log is not None:
            self._current_step_log.set_action(name, param_values)
        else:
            raise RuntimeError("Can't log an action start as no step has begun")

    def info(self, message, data=""):
        self.stdlogger.info(message + data)
        if self._current_step_log is not None:
            self._current_step_log.record_message(INFO, message, data)
        else:
            raise RuntimeError("Can't log a message as no step has begun")

    def warning(self, message, data=""):
        self.stdlogger.warning(message + data)
        if self._current_step_log is not None:
            self._current_step_log.record_message(WARNING, message, data)
        else:
            raise RuntimeError("Can't log a message as no step has begun")

    def error(self, message, data=""):
        self.stdlogger.error(message + data)
        if self._current_step_log is not None:
            self._current_step_log.record_message(ERROR, message, data)
        else:
            raise RuntimeError("Can't log a message as no step has begun")

    def get_last_message(self):
        if len(self.steps_log) > 0:
            last_step = self.steps_log[-1]
            if len(last_step.messages) > 0:
                return last_step.messages[-1]
        return None, None, None

    def dump(self):
        start_msecs = int(self.start_timestamp.timestamp() * 1000)
        end_msecs = int(self.end_timestamp.timestamp() * 1000)
        return {
            "startTime": start_msecs,
            "endTime": end_msecs,
            "result": self.result,
            "inputValidation": self.input_validation,
            "inputValidationMessage": self.input_validation_message,
            "outputValidation": self.output_validation,
            "outputValidationMessage": self.output_validation_message,
            "failure": self.failure,
            "failureStepIndex": self.failure_step_index,
            "failureMessage": self.failure_message,
            "steps": [step.dump() for step in self.steps_log],
        }


class StepLog(object):
    def __init__(self, step_index):
        self.step_index = step_index
        self.action_name = ""
        self.action_params_val = []  # [ (param_name, param_val), ]
        self.messages = []  # [ (level, message_text, data_text), ]

    def set_action(self, name, param_values):
        self.action_name = name
        self.action_params_val = param_values

    def record_message(self, level, message, data):
        self.messages.append((level, message, data))

    def dump(self):
        data = {
            "index": self.step_index,
            "actionName": self.action_name,
            "actionParamsVal": self.action_params_val,
            "messages": [],
        }
        for (level, msg, msg_data) in self.messages:
            data["messages"].append({"level": level, "message": msg, "data": msg_data})
        return data
