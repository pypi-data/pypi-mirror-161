from datetime import datetime
from typing import Optional, List


DEFAULT_CHANNEL_EVENTS = [
    "new_conversation",
    "conversation_initialized",
    "new call",
    "call ended"
    "user_online",
]

DEFAULT_CHANNEL_ACTIONS = [
    "hang_up",
    "dial"
]


def rasa_event_to_co_event(e: dict, channel_events: Optional[List[str]] = None):
    """Transforms an event in RASA format to the standard co format."""
    # First, we deal with the id and timestamp.
    dt = datetime.fromtimestamp(e["timestamp"])

    event = {
        "event_id": str(e["timestamp"]).replace(".", ""),
        "event_type": "",
        "event_data": {},
        "created_at": dt.isoformat()
    }

    if e["event"] == "user":
        # We need to look at parse data to determine if it's a synthetic event or not
        if e["parse_data"]["intent"]["name"].startswith("event_"):
            event_name = e["parse_data"]["intent"]["name"][6:]

            # We only transform the event if it's a channel one
            if event_name in DEFAULT_CHANNEL_EVENTS or event_name in (channel_events or []):
                event["event_type"] = event_name
                for entity in e["parse_data"]["entities"]:
                    event["event_data"].update({
                        entity["entity"]: entity["value"]
                    })
        else:
            event["event_type"] = "user_said"
            event["event_data"] = {
                "value": e["text"]
            }
    elif e["event"] == "bot":
        event["event_type"] = "bot_said"
        event["event_data"] = {
            "value": e["text"]
        }
    elif e["event"] == "action" and e["name"] == "action_listen":
        event["event_type"] = "action"
        event["event_data"] = {
            "action": "listen",
            "params": {}
        }
    elif e["event"] == "action" and e["name"] in DEFAULT_CHANNEL_ACTIONS:
        event["event_type"] = "action"

        # TODO: extract params if present
        event["event_data"] = {
            "action": e["name"],
            "params": {}
        }

    return event if event["event_type"] else None


def rasa_events_to_co_events(events: list, tracker: dict):
    """Transforms a full history of RASA events into co events.

    Events that don't have an equivalent are skipped.
    """
    channel_events = tracker["slots"].get("channel_events", [])
    co_events = []
    for event in events:
        co_event = rasa_event_to_co_event(event, channel_events)
        if co_event:
            co_events.append(co_event)

    return co_events
