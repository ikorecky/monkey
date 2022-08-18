import logging
from dataclasses import dataclass, field
from typing import Sequence

from marshmallow import Schema, fields, post_load

from common.credentials import Credentials, CredentialsSchema

from . import AbstractEvent

logger = logging.getLogger(__name__)


class CredentialsStolenEventSchema(Schema):
    source: fields.UUID()
    target: fields.UUID()  # TODO: Fix it later
    timestamp: fields.Float()
    tags: fields.List(fields.Nested(fields.Str()))
    stolen_credentials = fields.List(fields.Nested(CredentialsSchema))

    @post_load
    def _make_credentials_stolen_event(self, data, **kwargs):
        list_credentials = [Credentials.from_mapping(creds) for creds in data["stolen_credentials"]]
        return CredentialsStolenEvent(list_credentials)


@dataclass(frozen=True)
class CredentialsStolenEvent(AbstractEvent):
    """
    An event that occurs when an agent collects credentials from the victim

    Attributes:
        :param stolen_credentials: The credentials that were stolen by an agent
    """

    stolen_credentials: Sequence[Credentials] = field(default_factory=list)

    @staticmethod
    def from_dict(event_data):
        try:
            deserialized_data = CredentialsStolenEventSchema().load(event_data)
            return deserialized_data
        except Exception as err:
            logger.debug(f"Some kind of error happened: {err}")

    @staticmethod
    def to_dict(event):
        try:
            serialized_data = CredentialsStolenEventSchema().dump(event)
            return serialized_data
        except Exception as err:
            logger.debug(f"Some kind of error happened: {err}")
