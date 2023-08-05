""" In order to add support for actions to have parameters patch the ActionExecutor.run function."""
import logging
import typing
from typing import Text, Dict, Any, Optional

from rasa_sdk import utils
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import ActionNotFoundException

if typing.TYPE_CHECKING:  # pragma: no cover
    from rasa_sdk.types import ActionCall

logger = logging.getLogger(__name__)


async def run(self, action_call: "ActionCall") -> Optional[Dict[Text, Any]]:
    from rasa_sdk.interfaces import Tracker

    action_name = action_call.get("next_action")
    if action_name:
        logger.debug(f"Received request to run '{action_name}'")

        # If the action name has the form "name(parameters)" we extract them.
        parameters = None
        if "(" in action_name:
            action_name, _, parameters = action_name.partition("(")
            parameters = parameters.strip()
            assert parameters[-1] == ")"
            parameters = parameters[0:-1]

        action = self.actions.get(action_name)
        if not action:
            raise ActionNotFoundException(action_name)

        tracker_json = action_call["tracker"]
        domain = action_call.get("domain", {})
        tracker = Tracker.from_dict(tracker_json)
        dispatcher = CollectingDispatcher()

        if parameters:
            tracker.action_parameters = parameters

        events = await utils.call_potential_coroutine(
            action(dispatcher, tracker, domain)
        )

        if not events:
            # make sure the action did not just return `None`...
            events = []

        validated_events = self.validate_events(events, action_name)
        logger.debug(f"Finished running '{action_name}'")
        return self._create_api_response(validated_events, dispatcher.messages)

    logger.warning("Received an action call without an action.")
    return None
