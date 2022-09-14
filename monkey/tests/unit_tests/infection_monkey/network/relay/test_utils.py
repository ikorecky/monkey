import pytest
import requests
import requests_mock

from infection_monkey.network.relay.utils import find_server

SERVER_1 = "1.1.1.1:12312"
SERVER_2 = "2.2.2.2:4321"
SERVER_3 = "3.3.3.3:3142"
SERVER_4 = "4.4.4.4:5000"


servers = [SERVER_1, SERVER_2, SERVER_3, SERVER_4]


@pytest.mark.parametrize(
    "expected_server,server_response_pairs",
    [
        (None, [(server, {"exc": requests.exceptions.ConnectionError}) for server in servers]),
        (
            SERVER_2,
            [(SERVER_1, {"exc": requests.exceptions.ConnectionError})]
            + [(server, {"text": ""}) for server in servers[1:]],  # type: ignore[dict-item]
        ),
    ],
)
def test_find_server(expected_server, server_response_pairs):
    with requests_mock.Mocker() as mock:
        for server, response in server_response_pairs:
            mock.get(f"https://{server}/api?action=is-up", **response)

        assert find_server(servers) is expected_server


def test_find_server__multiple_successes():
    with requests_mock.Mocker() as mock:
        mock.get(f"https://{SERVER_1}/api?action=is-up", exc=requests.exceptions.ConnectionError)
        mock.get(f"https://{SERVER_2}/api?action=is-up", text="")
        mock.get(f"https://{SERVER_3}/api?action=is-up", text="")
        mock.get(f"https://{SERVER_4}/api?action=is-up", text="")

        assert find_server(servers) == SERVER_2
