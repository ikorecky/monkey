from common.credentials import Credentials, Password, Username
from common.events import CredentialsStolenEvent, CredentialsStolenSerializer

stolen_credentials = [
    Credentials(identity=Username("test_one"), secret=Password("secret_passowrd")),
    Credentials(identity=Username("test_two"), secret=Password("super_secret")),
]


def test_credentials_stolen_serializer():

    credentials_stolen_event = CredentialsStolenEvent(
        timestamp=1.0, stolen_credentials=stolen_credentials
    )
    print(credentials_stolen_event.timestamp)

    serialized_event = CredentialsStolenSerializer().serialize(credentials_stolen_event)
    import pprint

    pprint.pprint(serialized_event)
    deserialized_event = CredentialsStolenSerializer().deserialize(serialized_event)
    pprint.pprint(deserialized_event)

    assert serialized_event != deserialized_event
    assert deserialized_event == credentials_stolen_event
