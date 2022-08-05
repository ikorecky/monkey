from abc import ABC, abstractmethod
from typing import Any, Callable, Sequence

from common.events import AbstractEvent


class IEventQueue(ABC):
    """
    Manages subscription and publishing of events
    """

    @abstractmethod
    def subscribe_all(self, subscriber: Callable[..., Any]):
        """
        Subscribes a subscriber to all events

        :param subscriber: Callable that should subscribe to events
        """

        pass

    @abstractmethod
    def subscribe_types(self, types: Sequence[AbstractEvent], subscriber: Callable[..., Any]):
        """
        Subscribes a subscriber to all specifed event types

        :param types: Event types to which the subscriber should subscribe
        :param subscriber: Callable that should subscribe to events
        """

        pass

    @abstractmethod
    def subscribe_tags(self, tags: Sequence[str], subscriber: Callable[..., Any]):
        """
        Subscribes a subscriber to all specified event tags

        :param tags: Event tags to which the subscriber should subscribe
        :param subscriber: Callable that should subscribe to events
        """

        pass

    @abstractmethod
    def publish(self, event: AbstractEvent, data: Any):
        """
        Publishes an event with the given data

        :param event: Event to publish
        :param data: Data to pass to subscribers with the event publish
        """

        pass
