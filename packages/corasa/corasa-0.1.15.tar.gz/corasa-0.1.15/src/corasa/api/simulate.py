import asyncio
import uuid

import aiohttp


async def simulate():
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://127.0.0.1:8000/twilio/voice/a',
                                data={
                                    "CallSid": str(uuid.uuid4())
                                }) as response:
            pass


async def simulate_app():
    async with aiohttp.ClientSession() as session:
        host = "conversational-ai.live.bewell.uk"
        host = "localhost:8000"
        base_url = f"http://webchat:JzUjRAG76kbWKX9xHJ64tXuvz3asBrJz@{host}"
        async with session.post(f'{base_url}/conversations',
                                json={"context_data": {"name": "Mary", "voice": "Polly.Amy"},
                                      "webhook_url": "https://api.live.bewell.uk",
                                      "user_id": "41d070f6-a520-48fc-8a4c-b45ca70b95d4",
                                      "conversation_id": "60b0298e-3c21-4506-ad3d-342f8dc28cbd",
                                      "bot_id": "bewell-prod"}) as response:
            pass

        async with session.post(f'{base_url}/conversations/60b0298e-3c21-4506-ad3d-342f8dc28cbd/messages',
                                json={"from": "user",
                                      "message": "hi"}) as response:
            pass

        # async with session.post(f'{base_url}/conversations/60b0298e-3c21-4506-ad3d-342f8dc28cbd/events',
        #                         json={"event_type": "user_said",
        #                               "event_data": {"value": "hi"}}) as response:
        #     pass



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(simulate_app())
