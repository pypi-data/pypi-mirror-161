import asyncio
import json
import logging
import os
import secrets
from time import time
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi import Response, Form, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import rasa_api
from .models import ConversationData, EventData, MessageData
from .twilio_api import start_recording

log = logging.getLogger(__name__)

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)

security = HTTPBasic()

# Fetch the HTTP authentication information
BASIC_HTTP_AUTH = os.environ.get("BASIC_HTTP_AUTH")
CREDENTIALS = [item.split(":") for item in BASIC_HTTP_AUTH.split(",")]

WEBCHAT_KEY = [cred[1] for cred in CREDENTIALS
               if cred[0] == "webchat"][0]


def get_auth_key(credentials: HTTPBasicCredentials = Depends(security)):
    found = False

    for cred in CREDENTIALS:
        correct_username = secrets.compare_digest(credentials.username, cred[0])
        correct_password = secrets.compare_digest(credentials.password, cred[1])
        if correct_username and correct_password:
            found = True
            break

    if not found:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


_bot_id_cache = {}


async def _get_bot_id(conversation_id: str):
    """Returns the bot_id associated with a conversation."""
    tries = 0

    # We wait up to 5 seconds for it to appear in the cache
    while True:
        if conversation_id not in _bot_id_cache:
            if tries < 10:
                tries += 1
                await asyncio.sleep(0.5)
            else:
                raise Exception(f"Bot id for conversation {conversation_id} unknown.")

                # TODO: save the cache in a permanent storage so that it works with multiple
                #   instances.
        else:
            break

    return _bot_id_cache[conversation_id]


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/conversations")
async def create_conversation(conversation_data: ConversationData,
                              request: Request,
                              auth_key: str = Depends(get_auth_key)):
    """Creates a new conversation."""
    log.info(f"CREATE_CONVERSATION [{auth_key}] {request.url}")
    log.info(await request.body())

    conversation_id, events = await rasa_api.create_conversation(
        conversation_data.bot_id, conversation_data.dict()
    )

    # Update the cache
    _bot_id_cache[conversation_id] = conversation_data.bot_id

    return {
        "conversation_id": conversation_id,
        "status": "active",
        "participants": {
            "user": "",
            "bot": conversation_data.bot_id
        },
        "created_at": events[0]["created_at"]
    }


@app.post("/conversations/{conversation_id}/events")
async def add_event(conversation_id: str,
                    event_data: EventData,
                    request: Request,
                    wait_response: bool = False,
                    auth_key: str = Depends(get_auth_key)):
    """Adds a new event to a conversation."""
    log.info(f"ADD_EVENT [{auth_key}] {request.url}")
    log.info(await request.body())

    bot_id = await _get_bot_id(conversation_id)

    initial_events = await rasa_api.add_event(bot_id, conversation_id, event_data.dict())

    # If we need to wait for response, we run the reasoning
    if wait_response:
        events = await rasa_api.run_reasoning(bot_id, conversation_id)
    else:
        events = initial_events

    # Return the new events including the new one
    return list(reversed(events[len(initial_events) - 1:]))


@app.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str,
                      message_data: MessageData,
                      request: Request,
                      wait_response: bool = False,
                      auth_key: str = Depends(get_auth_key)):
    """Adds a new message to a conversation."""
    log.info(f"ADD_MESSAGE [{auth_key}] {request.url}")
    log.info(await request.body())

    bot_id = await _get_bot_id(conversation_id)

    raw_data = json.loads(request._body)
    initial_events = await rasa_api.add_event(bot_id, conversation_id, {
        "event_type": "user_said" if raw_data.get("from") == "user" else "bot_said",
        "event_data": {
            "value": message_data.message
        }
    })

    # If we need to wait for response, we run the reasoning
    if wait_response:
        events = await rasa_api.run_reasoning(bot_id, conversation_id)
    else:
        events = initial_events

    # Return the new events including the new one
    return list(reversed(events[len(initial_events) - 1:]))


@app.get("/conversations/{conversation_id}/events")
async def list_events(conversation_id: str,
                      request: Request,
                      wait_on_event_id: Optional[str] = None,
                      auth_key: str = Depends(get_auth_key)):
    log.info(f"[{auth_key}] {request.url}")
    log.info(await request.body())

    bot_id = await _get_bot_id(conversation_id)

    t0 = time()
    events = await rasa_api.list_events(bot_id, conversation_id)

    while (wait_on_event_id and events
            and events[-1]["event_id"] == wait_on_event_id and time() - t0 < 25):
        await asyncio.sleep(1)

        events = await rasa_api.list_events(bot_id, conversation_id)

    return list(reversed(events))


async def _post_and_reason(bot_id, conversation_id: str, event: dict):
    """Posts an event and runs the reasoning."""
    return await rasa_api.add_event(bot_id, conversation_id, event)


# noinspection PyPep8Naming
@app.post("/twilio/voice/{bot_id}")
async def twilio_voice(bot_id: str,
                       request: Request,
                       CallSid: str = Form(),
                       CallStatus: Optional[str] = Form(""),
                       From: Optional[str] = Form(""),
                       To: Optional[str] = Form(""),
                       SpeechResult: Optional[str] = Form(""),
                       Digits: Optional[str] = Form("")):
    conversation_id = CallSid
    t0 = time()
    log.info(f"Got new Twilio call for conversation {conversation_id}")
    log.info(request.url)

    # First, we need to determine if it's a new call
    tracker, initial_events = await rasa_api.get_tracker_and_events(bot_id, conversation_id)

    twilio_config = tracker["slots"].get("twilio")
    voice = twilio_config["voice"] or "Polly.Joanna-Neural"
    lang = twilio_config["lang"] or "en-US"

    # If we have only 1 event (which should be action_listen), it's a new call
    new_call = False
    if len(initial_events) == 1:
        # So, we post the new call event
        initial_events = await _post_and_reason(bot_id, conversation_id, {"event_type": "new_conversation"})
        new_call = True

    response_elements = []

    if CallStatus == "completed":
        await _post_and_reason(bot_id, conversation_id, {"event_type": "call ended"})
    else:
        if new_call:
            events = await _post_and_reason(bot_id, conversation_id, {
                "event_type": "new call",
                "event_data": {
                    "phone_number": From,
                    "called_phone_number": To
                }
            })
        else:
            _input = SpeechResult or Digits

            if _input:
                log.info(f"The user input was: '{_input}'")
                events = await _post_and_reason(bot_id, conversation_id, {
                    "event_type": "user_said",
                    "event_data": {
                        "value": _input
                    }
                })
            else:
                log.info("The user was silent.")
                events = await _post_and_reason(bot_id, conversation_id, {
                    "event_type": "user_silent",
                    "event_data": {}
                })

        new_events = events[len(initial_events):]

        for event in new_events:
            if event["event_type"] == "bot_said":
                text = event["event_data"]["value"]

                response_elements.append(f"""
                    <Say voice="{voice}" language="{lang}">
                                {text}
                            </Say>
                """)
            elif event["event_type"] == "action" and event["event_data"]["action"] == "hang_up":
                response_elements.append(f"""<Hangup/>""")

        # Last, we need to add the gather element
        defaults = {
            "input": "speech dtmf",
            "enhanced": "true",
            "hints": "",
            "timeout": 5,
            "speechTimeout": "auto",
            "speechModel": "phone_call",
            "language": lang
        }

        response_elements.append(f"""
            <Gather input="{defaults['input']}" 
                            enhanced="{defaults['enhanced']}" 
                            speechTimeout="{defaults['speechTimeout']}" 
                            speechModel="{defaults['speechModel']}"
                            timeout="{defaults['timeout']}"
                            hints="{defaults['hints']}"
                            actionOnEmptyResult="true" 
                            action="/twilio/voice/{bot_id}#e=dublin"
                            language="{defaults['language']}"/>
        """)

    response_elements_text = "\n".join(response_elements)
    data = f"""<Response>
        {response_elements_text}
        </Response>
        """

    log_data = data.replace("\n", " ")
    log.info(f"Twilio response in {time() - t0} ms:\n{log_data}")

    # If it's a new call, we also kick off the recording
    if new_call and twilio_config.get("call_recording"):
        loop = asyncio.get_running_loop()
        loop.create_task(start_call_recording(bot_id, conversation_id))

    return Response(content=data, media_type="application/xml")


async def start_call_recording(bot_id: str, conversation_id: str):
    loop = asyncio.get_running_loop()
    recording_id = await loop.run_in_executor(None, start_recording, conversation_id)

    await _post_and_reason(bot_id, conversation_id, {
        "event_type": "call recording started",
        "event_data": {
            "call_id": conversation_id,
            "call_recording_id": recording_id
        }
    })
    log.info(f"Successfully saved call recording in context {recording_id}.")


@app.get("/webchat/{bot_id}")
async def webchat(bot_id: str, auth_key: str = Depends(get_auth_key)):
    log.info(f"[{auth_key}] Got request for webchat for bot {bot_id}")

    data = f"""
<!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WebChat</title>

  <style>
    body {{
      color: #ffffff !important;
      padding: 0;
      margin: 0;
    }}

    .content {{
      padding-top: 200px;
      max-width: 60%;
      padding-right: 150px;
      margin: auto;
      color: black;
    }}
  </style>

</head>

<body>
  <div class="cover"></div>
  <div class="content">
    <div id="webchat"
         data-widget="web-chat"
         data-prop-api-url="/"
         data-prop-api-key-id="webchat"
         data-prop-api-key-secret="{WEBCHAT_KEY}"
         data-prop-assistant-id="{bot_id}"
         data-prop-assistant-name="WebChat"
         data-prop-welcome-message=""

         data-prop-assistant-avatar=""
         data-prop-assistant-avatar-margin-top=""
         data-prop-logo-size=""
         data-prop-color=""

         data-prop-auto-toggle="true"
         data-prop-auto-toggle-delay="500"
         data-prop-message-rate-delay="1000"
         data-prop-width="400"
         data-prop-position="inline"
         data-prop-embedded="false"

         data-prop-live-log-mode="test"
         data-prop-welcome-message="Hey there!"
         data-prop-persist-session="false"
         data-prop-fullscreen="false"/>
  </div>
  <div></div>
  <script type="application/javascript">
    let elem = document.getElementById('webchat');
    elem.setAttribute("data-prop-api-url", window.location.origin);
  </script>
  <script src="https://static.colang.ai/webchat.js"></script>
</body>
</html>
"""

    return Response(content=data, media_type="text/html")
