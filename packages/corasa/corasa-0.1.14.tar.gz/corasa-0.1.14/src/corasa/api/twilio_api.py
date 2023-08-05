import logging
import os
import time

from twilio.rest import Client

log = logging.getLogger(__name__)


def start_recording(conversation_id: str):
    """Starts the recording for the specified conversation.

    We start with a small delay to allow for the resource to be properly created.
    """
    time.sleep(0.25)

    twilio_account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    twilio_auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    twilio_client = Client(twilio_account_sid, twilio_auth_token)

    recording = twilio_client.calls(conversation_id).recordings.create()

    log.info(f"Call recording for {conversation_id} started.")
    return recording.sid
