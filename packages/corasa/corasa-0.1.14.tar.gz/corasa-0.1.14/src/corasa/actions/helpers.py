import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .util import eval_expr

log = logging.getLogger(__name__)


class ActionContext:
    """Context object that is passed to actions."""
    def __init__(self, dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]):
        self.dispatcher = dispatcher
        self.tracker = tracker
        self.domain = domain

        # We keep track of all the new slots that are set
        self.action_events = []
        self.new_slots = {}

    async def get(self, key, default_value=None):
        """Returns the value of a slot."""
        if key in self.new_slots:
            value = self.new_slots[key]
        else:
            value = self.tracker.get_slot(key)

        if value is None:
            value = default_value

        return value

    async def set(self, key, value):
        """Sets the value of a slot."""
        self.new_slots[key] = value

    async def update(self, d):
        """Updates the context by setting the slots specified in the dict."""
        self.new_slots.update(d)

    def add_event(self, event: any):
        self.action_events.append(event)

    def get_slot_set_events(self):
        """Computes the slot_set event with all the values."""

        events = []
        for k, v in self.new_slots.items():
            events.append(SlotSet(k, v))

        return events


def action(action_name: str):
    """Decorator for registering an action with the specified name.

    The parameters of the action are loaded from the `action_params` slot.
    There is basic support to fetch the value of some parameters from other context
    variables.

    The return value of the action is set into the `action_result`.

    :param action_name: The name under which the action should be registered.
    """

    def decorator(func):
        log.debug(f"Registering action '{action_name}' ...")

        action_class = type(f"Action_{action_name}", (Action,), {})

        def name(self) -> Text:
            return action_name

        action_class.name = name

        async def run(self, dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            # We extract the action params
            action_params = tracker.get_slot("action_params") or {}

            # We go through them and if there are references to other slots, we fill them in
            for key, value in list(action_params.items()):
                if isinstance(value, str) and value[0] == "$" and value[1] != "$":
                    action_params[key] = eval_expr(tracker, value)

            # We invoke the action
            ctx = ActionContext(dispatcher, tracker, domain)
            action_result = await func(ctx, **action_params)

            ctx.new_slots["action_result"] = action_result

            # If there were any slots set, we also generate events for them.
            slot_set_events = ctx.get_slot_set_events()

            return slot_set_events + ctx.action_events

        action_class.run = run

        return action_class

    return decorator
