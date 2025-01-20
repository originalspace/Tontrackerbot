import asyncio 
import websockets
import json

# async def handler():
    

async def subscribe(): 
    uri = "wss://pumpportal.fun/api/data"
    async with websockets.connect(uri) as websocket:

        payload = {
            "method": "subscribeAccountTrade",
            "keys": ["4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"]
        }
        await websocket.send(json.dumps(payload))
        
        async for message in websocket:
            print(json.loads(message))
            




asyncio.get_event_loop().run_until_complete(subscribe())


