import logging
import socket
from contextlib import suppress
from ipaddress import IPv4Address
from typing import Dict, Iterable, Iterator, MutableMapping, Optional

import requests

from common.common_consts.timeouts import MEDIUM_REQUEST_TIMEOUT
from common.network.network_utils import address_to_ip_port
from infection_monkey.network.relay import RELAY_CONTROL_MESSAGE_REMOVE_FROM_WAITLIST
from infection_monkey.utils.threading import (
    ThreadSafeIterator,
    create_daemon_thread,
    run_worker_threads,
)

logger = logging.getLogger(__name__)

# The number of Island servers to test simultaneously. 32 threads seems large enough for all
# practical purposes. Revisit this if it's not.
NUM_FIND_SERVER_WORKERS = 32


def find_server(servers: Iterable[str]) -> Optional[str]:
    server_list = list(servers)
    server_iterator = ThreadSafeIterator(server_list.__iter__())
    server_results: Dict[str, bool] = {}

    run_worker_threads(
        _find_island_server,
        "FindIslandServer",
        args=(server_iterator, server_results),
        num_workers=NUM_FIND_SERVER_WORKERS,
    )

    for server in server_list:
        if server_results[server]:
            return server

    return None


def _find_island_server(servers: Iterator[str], server_status: MutableMapping[str, bool]):
    with suppress(StopIteration):
        server = next(servers)
        server_status[server] = _check_if_island_server(server)


def _check_if_island_server(server: str) -> bool:
    logger.debug(f"Trying to connect to server: {server}")

    try:
        requests.get(  # noqa: DUO123
            f"https://{server}/api?action=is-up",
            verify=False,
            timeout=MEDIUM_REQUEST_TIMEOUT,
        )

        return True
    except requests.exceptions.ConnectionError as err:
        logger.error(f"Unable to connect to server/relay {server}: {err}")
    except TimeoutError as err:
        logger.error(f"Timed out while connecting to server/relay {server}: {err}")
    except Exception as err:
        logger.error(
            f"Exception encountered when trying to connect to server/relay {server}: {err}"
        )

    return False


def send_remove_from_waitlist_control_message_to_relays(servers: Iterable[str]):
    for server in servers:
        t = create_daemon_thread(
            target=_send_remove_from_waitlist_control_message_to_relay,
            name="SendRemoveFromWaitlistControlMessageToRelaysThread",
            args=(server,),
        )
        t.start()


def _send_remove_from_waitlist_control_message_to_relay(server: str):
    ip, port = address_to_ip_port(server)
    notify_disconnect(IPv4Address(ip), int(port))


def notify_disconnect(server_ip: IPv4Address, server_port: int):
    """
    Tell upstream relay that we no longer need the relay.

    :param server_ip: The IP address of the server to notify.
    :param server_port: The port of the server to notify.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as d_socket:
        try:
            d_socket.connect((server_ip, server_port))
            d_socket.sendall(RELAY_CONTROL_MESSAGE_REMOVE_FROM_WAITLIST)
            logger.info(f"Control message was sent to the server/relay {server_ip}:{server_port}")
        except OSError as err:
            logger.error(f"Error connecting to socket {server_ip}:{server_port}: {err}")
