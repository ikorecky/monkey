import logging
import random
import shutil
import string
import subprocess

from common.common_consts.post_breach_consts import POST_BREACH_COMMUNICATE_AS_BACKDOOR_USER
from infection_monkey.i_puppet.i_puppet import PostBreachData
from infection_monkey.post_breach.pba import PBA
from infection_monkey.utils.auto_new_user_factory import create_auto_new_user
from infection_monkey.utils.environment import is_windows_os
from infection_monkey.utils.new_user_error import NewUserError
from infection_monkey.utils.random_password_generator import get_random_password

INFECTION_MONKEY_WEBSITE_URL = "https://infectionmonkey.com/"

CREATED_PROCESS_AS_USER_SUCCESS_FORMAT = (
    "Created process '{}' as user '{}' and the process succeeded."
)
CREATED_PROCESS_AS_USER_FAILED_FORMAT = (
    "Created process '{}' as user '{}', but the process failed (exit status {}:{})."
)

USERNAME_PREFIX = "somenewuser"

logger = logging.getLogger(__name__)


class CommunicateAsBackdoorUser(PBA):
    """
    This PBA creates a new user, and then creates HTTPS requests as that user. This is used for a
    Zero Trust test of the People pillar. See the relevant telemetry processing to see what findings
    are created.
    """

    def __init__(self):
        super(CommunicateAsBackdoorUser, self).__init__(
            name=POST_BREACH_COMMUNICATE_AS_BACKDOOR_USER
        )

    def run(self):
        username = CommunicateAsBackdoorUser.get_random_new_user_name()
        try:
            password = get_random_password(14)
            with create_auto_new_user(username, password) as new_user:
                http_request_commandline = (
                    CommunicateAsBackdoorUser.get_commandline_for_http_request(
                        INFECTION_MONKEY_WEBSITE_URL
                    )
                )
                exit_status = new_user.run_as(http_request_commandline)
                result = CommunicateAsBackdoorUser._get_result_for_telemetry(
                    exit_status, http_request_commandline, username
                )
                # `command` is empty here; we could get the command from `new_user` but that
                # doesn't work either since Windows doesn't use a command, it uses win32 modules
                self.pba_data.append(PostBreachData(self.name, self.command, result))
        except subprocess.CalledProcessError as e:
            self.pba_data.append(
                PostBreachData(self.name, self.command, (e.output.decode(), False))
            )
        except NewUserError as e:
            self.pba_data.append(PostBreachData(self.name, self.command, (str(e), False)))
        finally:
            return self.pba_data

    @staticmethod
    def get_random_new_user_name():
        return USERNAME_PREFIX + "".join(
            random.choice(string.ascii_lowercase) for _ in range(5)  # noqa: DUO102
        )

    @staticmethod
    def get_commandline_for_http_request(url, is_windows=is_windows_os()):
        if is_windows:
            format_string = (
                'powershell.exe -command "[Net.ServicePointManager]::SecurityProtocol = ['
                "Net.SecurityProtocolType]::Tls12; "
                'Invoke-WebRequest {url} -UseBasicParsing -method HEAD"'
            )
        else:
            # if curl works, we're good.
            # If curl doesn't exist or fails and wget work, we're good.
            # And if both don't exist: we'll call it a win.
            if shutil.which("curl") is not None:
                format_string = "curl {url} --head --max-time 10"
            else:
                format_string = "wget -O/dev/null -q {url} --method=HEAD --timeout=10"
        return format_string.format(url=url)

    @staticmethod
    def _get_result_for_telemetry(exit_status, commandline, username):
        if exit_status == 0:
            result = (CREATED_PROCESS_AS_USER_SUCCESS_FORMAT.format(commandline, username), True)
        else:
            result = (
                CREATED_PROCESS_AS_USER_FAILED_FORMAT.format(
                    commandline, username, exit_status, twos_complement(exit_status)
                ),
                False,
            )

        return result


def twos_complement(exit_status):
    return hex(exit_status & (2 ** 32 - 1))
