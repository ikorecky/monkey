import logging
from dataclasses import dataclass, field
from typing import Sequence

from marshmallow import Schema, fields, post_load

from common.credentials import Credentials, CredentialsSchema

from . import AbstractEvent

logger = logging.getLogger(__name__)


class CredentialsStolenEventSchema(Schema):
    source = fields.Int()
    target = fields.UUID(allow_none=True)  # TODO: Fix it later
    timestamp = fields.Float()
    tags = fields.List(fields.Nested(fields.Str()))
    stolen_credentials = fields.List(fields.Nested(CredentialsSchema))

    @post_load
    def _make_credentials_stolen_event(self, data, **kwargs):
        stolen_credentials = [Credentials(**c) for c in data["stolen_credentials"]]
        data["stolen_credentials"] = stolen_credentials
        data["tags"] = frozenset(data["tags"])

        return CredentialsStolenEvent(**data)


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
        return CredentialsStolenEventSchema().load(event_data)

    @staticmethod
    def to_dict(event):
        return CredentialsStolenEventSchema().dump(event)
