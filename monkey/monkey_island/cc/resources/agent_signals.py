import logging
from http import HTTPStatus
from json import JSONDecodeError

from flask import request

from monkey_island.cc.event_queue import IIslandEventQueue, IslandEventTopic
from monkey_island.cc.models import AgentSignals as Signals
from monkey_island.cc.resources.AbstractResource import AbstractResource

logger = logging.getLogger(__name__)


class AgentSignals(AbstractResource):
    urls = ["/api/agent-signals/terminate-all", "/api/agent-signals/<string:agent_id>"]

    def __init__(
        self,
        island_event_queue: IIslandEventQueue,
    ):
        self._island_event_queue = island_event_queue

    def post(self):
        try:
            signal = Signals(**request.json)

            if signal.terminate is None:
                raise ValueError("Terminate signal's timestamp is empty")
            self._island_event_queue.publish(IslandEventTopic.TERMINATE_AGENTS, signal=signal)
        except (JSONDecodeError, TypeError, ValueError) as err:
            return {"error": err}, HTTPStatus.BAD_REQUEST

        return {}, HTTPStatus.NO_CONTENT

    def get(self, agent_id: str):
        # TODO: return AgentSignals
        return {}, HTTPStatus.OK
