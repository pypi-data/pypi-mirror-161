#!/bin/false
# -*- coding: utf-8 -*-
from typing import Optional
import uuid

PTUTILS_NAMESPACE_UUID = uuid.UUID('1a57b5aa-db20-48ff-99dd-590fe2b86f61')


def parse_uuid(text: str) -> uuid.UUID:
    """
    Return a UUID object parsed from a UUID string of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.

    Parameters
    ----------
    text : str
        A UUID string of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.

    Returns
    -------
    uuid.UUID
        A UUID object
    """
    return uuid.UUID(text)


def random_uuid():
    """ Return a random uuid. """
    return uuid.uuid4()


def uuid_from_name(name: str, namespace_uuid: Optional[ uuid.UUID ] = PTUTILS_NAMESPACE_UUID):
    """ Return a stable uuid generated from the hash of a string. """
    if namespace_uuid is None:
        namespace_uuid = PTUTILS_NAMESPACE_UUID
    return uuid.uuid5( namespace_uuid, name )
