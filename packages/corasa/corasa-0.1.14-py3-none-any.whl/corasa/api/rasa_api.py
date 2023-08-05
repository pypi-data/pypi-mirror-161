"""Wrapper for the RASA API."""
import json
import logging
import os
import uuid
from typing import Optional

import aiohttp

from .utils import rasa_events_to_co_events

log = logging.getLogger(__name__)

# The URLs on which the RASA servers are listening.
RASA_SERVERS = os.environ.get("RASA_SERVERS", "default=127.0.0.1:5005")
BOT_API_URL = dict([(item.split("=")[0], item.split("=")[1])
                    for item in RASA_SERVERS.split(",")])
BOT_API_URL["default"] = "127.0.0.1:5005"

print(f"RASA Servers: {json.dumps(BOT_API_URL)}")


def _get_bot_api_url(bot_id: str):
    api_url = BOT_API_URL.get(bot_id, BOT_API_URL["default"])
    if not api_url.startswith("http"):
        api_url = f"http://{api_url}"

    return api_url


async def rasa_api_get(bot_id: str, endpoint: str):
    """Performs a GET call to the RASA HTTP server."""
    api_url = _get_bot_api_url(bot_id)

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{api_url}{endpoint}') as response:
            return await response.json()


async def rasa_api_post(bot_id: str, endpoint: str, data: Optional[dict] = None):
    """Performs a POST call to the RASA HTTP server."""
    api_url = _get_bot_api_url(bot_id)

    async with aiohttp.ClientSession() as session:
        url = f'{api_url}{endpoint}'
        async with session.post(url, json=data) as response:
            log.debug(f"RASA call to {url} returned status: {response.status}")

            return await response.json()


def _reinforces(intent_a: str, intent_b: str) -> bool:
    return intent_a in intent_b or intent_b in intent_a


def _update_intent_confidence(result):
    """Computes the right intent confidence based on the data coming from the NLU server.

    The data has the format:
    {
        "text": "",
        "intent": {
           "id": 517191430183595825,
           "name": "express_greeting_hello",
           "confidence": 0.7905938625335693
          },
          "entities": [],
          "intent_ranking": [
           {
            "id": 517191430183595825,
            "name": "express_greeting_hello",
            "confidence": 0.7905938625335693
           },
           ...
           ]
        }
    }
    """
    i = 1
    intent = result["intent_ranking"][0]["name"]

    while i < len(result["intent_ranking"]):
        additional_intent = result["intent_ranking"][i]

        if intent in additional_intent["name"] or additional_intent["name"] in intent:
            print(f"Updated confidence for `{intent}` "
                  f"using {additional_intent['name']}: "
                  f"+{additional_intent['confidence']}")

            result["intent"]["confidence"] += additional_intent["confidence"]

        i += 1


async def _compute_custom_features(bot_id, conversation_id):
    """Computes the custom features at a specific point in the conversation.

    We use the data stored in the `nlu_custom_features` slot and the last `utter_*`.
    """
    tracker = await rasa_api_get(bot_id, f"/conversations/{conversation_id}/tracker")

    last_utter = None
    i = len(tracker["events"])
    while i > 0:
        i -= 1
        event = tracker["events"][i]
        if event["event"] == "action" and event["name"].startswith("utter_"):
            last_utter = event["name"]
            break

    if last_utter is None:
        return None

    nlu_custom_features = tracker["slots"].get("nlu_custom_features", {})

    # We try to identify if there is a custom feature associated with the last utter
    for item in nlu_custom_features.values():
        if last_utter in item["after"]:
            return item["code"]

    return None


async def add_event(bot_id: str, conversation_id: str, event: dict):
    """Adds a new event to the RASA conversation.

    For events different than user_said, we add a synthetic user intent 'event'.
    """
    if "event_data" not in event:
        event = {
            **event,
            "event_data": {}
        }
    if event["event_type"] == "user_said":
        text = event["event_data"]["value"]
        parse_text = text

        # We compute the custom features before parsing
        custom_feature = await _compute_custom_features(bot_id, conversation_id)
        if custom_feature:
            log.info(f"Found custom feature {custom_feature} for {text}")
            parse_text += " " + custom_feature

        # First, we use the NLU endpoint to parse the data
        result = await rasa_api_post(bot_id, f"/model/parse", data={
            "text": parse_text,
        })

        _update_intent_confidence(result)

        # If the confidence is below 0.5, we transform it into "unknown_intent"
        if result["intent"]["confidence"] < 0.5:
            result["intent"]["name"] = "unknown_intent"
            result["intent"]["confidence"] = 1 - result["intent"]["confidence"]
            result["entities"] = []

        # We also add the hardcoded "entities" entity with all the values from
        # the latest intent.
        entities_dict = {}
        for entity in result["entities"]:
            entities_dict[entity["entity"]] = entity["value"]

        result["entities"].append({
            "start": 0,
            "end": 0,
            "entity": "entities",
            "value": entities_dict
        })

        log.info(f"NLU result: {json.dumps(result)}.")

        await rasa_api_post(bot_id, f"/conversations/{conversation_id}/tracker/events", data={
            "event": "user",
            "text": text,
            "parse_data": {
                "intent": result["intent"],
                "entities": result["entities"],
                "text": text
            }
        })
    else:
        # Create the synthetic intent.
        text = json.dumps(event)

        # For events, we only set the `event` entity.
        entities = [{
            "start": 0,
            "end": 0,
            "entity": "event_data",
            "value": event["event_data"]
        }]

        await rasa_api_post(bot_id, f"/conversations/{conversation_id}/tracker/events", data={
            "event": "user",
            "text": text,
            "parse_data": {
                "intent": {
                    "name": f"event_{event['event_type']}",
                    "confidence": 1.0
                },
                "entities": entities,
                "text": text
            }
        })

    events = await run_reasoning(bot_id, conversation_id)

    return events


async def create_conversation(bot_id: str, conversation_data: dict):
    """Creates a new conversation using the RASA API.

    We do this by posting the "new_conversation" event.
    """
    conversation_id = conversation_data.get("conversation_id", str(uuid.uuid4()))

    log.info(f"Creating new conversation {conversation_id}")
    events = await add_event(bot_id, conversation_id, {
        "event_type": "new_conversation",
        "event_data": conversation_data
    })

    return conversation_id, events


async def list_events(bot_id: str, conversation_id: str):
    """Returns the list of events for the given conversation."""
    tracker = await rasa_api_get(bot_id, f"/conversations/{conversation_id}/tracker")

    return rasa_events_to_co_events(tracker["events"], tracker)


async def get_tracker_and_events(bot_id: str, conversation_id: str):
    """Returns the full tracker for the given conversation."""
    tracker = await rasa_api_get(bot_id, f"/conversations/{conversation_id}/tracker")
    events = rasa_events_to_co_events(tracker["events"], tracker)

    return tracker, events


async def run_reasoning(bot_id: str, conversation_id: str):
    """Predicts and executes the next action until action_listen."""
    log.info(f"Running reasoning for conversation {conversation_id}")
    while True:
        res = await rasa_api_post(bot_id, f"/conversations/{conversation_id}/predict")

        next_action = res["scores"][0]["action"]
        log.info(f"Next action is {next_action}")

        # At action_listen, we check if we need to live log
        if next_action == "action_listen":
            # TODO: optimize this?
            tracker = await rasa_api_get(bot_id, f"/conversations/{conversation_id}/tracker")
            if tracker["slots"].get("live_log") or True:
                await rasa_api_post(bot_id, f"/conversations/{conversation_id}/execute", data={
                    "name": "live_log",
                    "policy": res["policy"],
                    "confidence": 1.0
                })
                await rasa_api_post(bot_id, f"/conversations/{conversation_id}/tracker/events", data={
                    "event": "undo"
                })

        await rasa_api_post(bot_id, f"/conversations/{conversation_id}/execute", data={
            "name": next_action,
            "policy": res["policy"],
            "confidence": res["confidence"]
        })

        if next_action == "action_listen":
            break

    _, events = await get_tracker_and_events(bot_id, conversation_id)
    return events
