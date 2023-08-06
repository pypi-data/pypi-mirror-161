# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Represents the messages passed between AMQ queues."""
import json
from typing import List, Optional, Union
from pydantic import BaseModel

from autoreduce_utils.message.validation import stages


class Message(BaseModel):
    """
    A class that represents a message to be sent via Kafka.
    Messages can be serialised and deserialised to and from JSON.
    """
    description: str = ""
    facility: str = "ISIS"
    run_number: Union[int, List[int], None] = None
    run_title: Union[str, List[str], None] = None
    instrument: Optional[str] = None
    rb_number: Union[int, str, None] = None
    started_by: Optional[int] = None
    data: Union[str, List[str], None] = None
    overwrite: Optional[bool] = None
    run_version: Optional[str] = None
    job_id: Optional[int] = None
    reduction_script: Optional[str] = None
    reduction_arguments: Optional[dict] = {}
    reduction_log: str = ""  # Cannot be null in database
    admin_log: str = ""  # Cannot be null in database
    message: Optional[str] = None
    retry_in: Optional[int] = None
    reduction_data: Optional[str] = None  # Required by reduction runner
    software: dict = {}
    flat_output: bool = False

    def serialize(self, indent=None, limit_reduction_script=False):
        """
        Serialized member variables as a JSON dump.

        Args:
            indent: The indent level passed to `json.dumps`.
            limit_reduction_script: If True, limit reduction_script to 50 chars
            in return.

        Returns:
            JSON dump of a dictionary representing the member variables.
        """
        data_dict = self.dict()
        if limit_reduction_script:
            data_dict["reduction_script"] = data_dict["reduction_script"][:50]

        return json.dumps(data_dict, indent=indent)

    @staticmethod
    def deserialize(serialized_object):
        """
        Deserialize an object and return a dictionary of that object.

        Args:
            serialized_object: The object to deserialize.

        Returns:
            Dictionary of deserialized object.
        """
        return json.loads(serialized_object)

    def populate(self, source, overwrite=True):
        """
        Populate the class from either a serialised object or a dictionary
        optionally retaining or overwriting existing values of attributes.

        Args:
            source: Object to populate class from.
            overwrite: If True, overwrite existing values of attributes.

        Raises:
            ValueError: If unable to recognise the serialised object.
            ValueError: If an unexpected key is encountered during message
            population.
        """
        if isinstance(source, str):
            try:
                source = self.deserialize(source)
            except json.decoder.JSONDecodeError as exp:
                raise ValueError(f"Unable to recognise serialized object {source}") from exp

        self_dict = self.dict()
        for key, value in source.items():
            if key in self_dict.keys():
                self_value = self_dict[key]
                if overwrite or self_value is None:
                    # Set the value of the variable on this object accessing it
                    # by name
                    setattr(self, key, value)
            else:
                raise ValueError(f"Unexpected key encountered during Message population: '{key}'.")

    def validate(self, destination: str):
        """
        Ensure that the message is valid to be sent to a given destination
        queue.

        Args:
            destination: The name of the queue to send the data to.
        """
        if destination == 'data_ready':
            stages.validate_data_ready(self)

    def to_dict(self):
        """Return the message as a Python dictionary."""
        return self.dict()
