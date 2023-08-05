from datetime import datetime, timezone
from typing import Any, Text, Dict, List

import rasa_sdk.events
from .util import eval_expr
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class InitializeConversation(Action):

    def name(self) -> Text:
        return 'initialize_conversation'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        events = []

        # We read the information from the "new_conversation" event
        event = tracker.get_slot("event_data")

        context_updates = {}
        if "bot_id" in event:
            context_updates["config.live_bot_name"] = event["bot_id"]
        if "user_id" in event:
            context_updates["user_id"] = event["user_id"]
        if "authenticated_user_id" in event:
            context_updates["authenticated_user_id"] = event["authenticated_user_id"]
        if "context_data" in event and isinstance(event["context_data"], dict):
            context_updates.update(event["context_data"])

        for k, v in context_updates.items():
            events.append(SlotSet(k, v))

        # We also set the current date and time for the conversation
        now = datetime.now(timezone.utc).astimezone().isoformat()
        events.append(SlotSet("system_datetime", now[0:26]))
        events.append(SlotSet("system_date", now[0:10]))
        events.append(SlotSet("system_time", now[11:26]))

        # We set the `eval` slot to the truthful value of the expression.
        events.extend([
            rasa_sdk.events.ActionExecuted(action_name="action_listen"),
            rasa_sdk.events.UserUttered(
                text="conversation_initialized",
                parse_data={
                    "intent": {
                        "name": "event_conversation_initialized",
                        "confidence": 1.0
                    },
                    "entities": []
                }
            )
        ])

        return events


class HangUp(Action):

    def name(self) -> Text:
        return 'hang_up'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return []


class Eval(Action):

    def name(self) -> Text:
        return 'eval'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not hasattr(tracker, "action_parameters"):
            raise Exception("No action parameters found in tracker.")

        expr = getattr(tracker, "action_parameters")
        result = eval_expr(tracker, expr)

        # We set the `eval` slot to the truthful value of the expression.
        return [
            SlotSet(key="eval", value=True if result else False),
        ]


class Set(Action):

    def name(self) -> Text:
        return 'set'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not hasattr(tracker, "action_parameters"):
            raise Exception("No action parameters found in tracker.")

        var_name, _, expr = getattr(tracker, "action_parameters").partition("=")
        var_name = var_name.strip().replace("$", "")
        val = eval_expr(tracker, expr)

        return [
            SlotSet(key=var_name, value=val),
        ]


class Push(Action):

    def name(self) -> Text:
        return 'push'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not hasattr(tracker, "action_parameters"):
            raise Exception("No action parameters found in tracker.")

        return_stack = tracker.slots.get("return_stack")
        assert isinstance(return_stack, list)

        return_point = getattr(tracker, "action_parameters")
        return_stack.append(return_point)

        print("Updated return stack to: ", return_stack)

        return [
            SlotSet(key="return_stack", value=return_stack),
        ]


class Call(Action):

    def name(self) -> Text:
        return 'call'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return []


class Pop(Action):

    def name(self) -> Text:
        return 'pop'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return_stack = tracker.slots.get("return_stack")
        assert isinstance(return_stack, list)

        # If we have action parameters, we're dealing with a specific pop, and we don't
        # need to do anything.
        if not hasattr(tracker, "action_parameters"):
            # If we have something left in the return stack, we use it.
            if return_stack:
                return_point = return_stack.pop()

                return [
                    SlotSet(key="return_stack", value=return_stack),
                    rasa_sdk.events.FollowupAction(f"pop({return_point})")
                ]

        return []


class CreateEvent(Action):

    def name(self) -> Text:
        return 'create_event'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not hasattr(tracker, "action_parameters"):
            raise Exception("No action parameters found in tracker.")

        # TODO: add support for additional event parameters.
        event_type = getattr(tracker, "action_parameters")

        return [
            rasa_sdk.events.ActionExecuted(action_name="action_listen"),
            rasa_sdk.events.UserUttered(
                text=event_type,
                parse_data={
                    "intent": {
                        "name": "event",
                        "confidence": 1.0
                    },
                    "entities": [
                        {
                            "entity": "event_type",
                            "start": 0,
                            "end": 9,
                            "value": event_type,
                        }
                    ]
                }
            )
        ]
