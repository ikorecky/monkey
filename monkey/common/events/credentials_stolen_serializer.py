from . import CredentialsStolenEvent, IEventSerializer


class CredentialsStolenSerializer(IEventSerializer):
    def serialize(self, event: CredentialsStolenEvent):
        if not issubclass(event.__class__, CredentialsStolenEvent):
            raise TypeError(f"Event must be of type: {CredentialsStolenEvent.__name__}")

        return CredentialsStolenEvent.to_dict(event)

    def deserialize(self, serialized_event) -> CredentialsStolenEvent:

        return CredentialsStolenEvent.from_dict(serialized_event)
