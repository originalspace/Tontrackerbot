from TonTools import *
import typing 
from pytonapi import *
from pytonapi.schema.events import TransactionEventData
import logging
import asyncio
from pytonapi.utils import raw_to_userfriendly
from dexscreener import DexscreenerClient

from telegram.ext import (
    Application, 
    PicklePersistence,
)


# Ignore warning message
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)



# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


TOKEN: typing.Final = ''
TEXT_CHAT_ID: typing.Final = ""
API_KEY: typing.Final = ''
CLIENT = TonCenterClient()
CLIENT2 = TonApiClient()
TON_USD_PRICE_URL = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"



# TON USD PRICE
response = requests.get(TON_USD_PRICE_URL)
data = json.loads(response.text)
TON_USD_PRICE = data['rates']['TON']['prices']['USD']

# List of wallets
wallet_list = ["EQB3ncyBUTjZUA5EnFKR5_EnOMI9V1tTEAAPaiU71gc4TiUt"]  

# Sends notifs
async def handler(event: TransactionEventData, tonapi: AsyncTonapi) -> None:
    trace = await tonapi.traces.get_trace(event.tx_hash)

    if trace.transaction.success:
        
        # from ticker
        jetton = JettonWallet((raw_to_userfriendly(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["dest"])),provider=CLIENT)
        await jetton.update()
        jetton_wallet = Jetton(jetton.to_dict()['jetton_master_address'], provider=CLIENT).to_dict()["address"]
        jetton_name = await tonapi.jettons.get_info(jetton_wallet)
     
        # to ticker
        jetton_to = JettonWallet((raw_to_userfriendly(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["value"]["token_wallet"])),provider=CLIENT)
        await jetton_to.update()
        jetton_to_wallet = Jetton(jetton_to.to_dict()["jetton_master_address"], provider=CLIENT).to_dict()["address"]
        jetton_to_name = await tonapi.jettons.get_info(account_id=jetton_to_wallet)

        # wallet balance
        wallet_balance = await Wallet(provider=CLIENT, address=(trace.transaction.account.address.to_userfriendly())).get_balance()

        # jetton info
        pairs = await DexscreenerClient().get_token_pairs_async(jetton_to_wallet)
        pair = pairs[0]
        dex = pair.dex_id
        address = pair.base_token.address
        symbol = pair.base_token.symbol
        mc = pair.fdv
        price = pair.price_usd 
        price_ton = pair.price_native
        change = pair.price_change
        m5 = change.m5
        h1 = change.h1
        h6 = change.h6
        h24 = change.h24
        h6_count = pair.transactions.h24
        age = pair.pair_created_at.date()
            
        if jetton_name.metadata.symbol == "pTON":
            if round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2) >= 1:
                if not jetton_to_name.metadata.symbol == "USD₮":
                    if int(mc) >= 1000000000:
                        text = (  
                    f"🌟Buy: {symbol}\n" 
                    f"on {dex}\n" 
                    #f"\n🌟 Transfer: {trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["sum_type"]}"
                    #f"\nType: {trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["sum_type"]}\n"
                    f"\n🔹Wallet: {trace.transaction.account.address.to_userfriendly()}"
                    f"\n🔹Amount: {round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)}" + f" {jetton_name.metadata.symbol}" + f" (${round((round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)*(round(TON_USD_PRICE,2))),2)})"
                    #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
                    #f"\nfor {round((10**-9*float((trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["value"]["min_out"]))),2)} {jetton_to_name.metadata.symbol}\n\n"       
                    f"\n\nmc: ${round((int(mc) * 10**-9), 1)}B\n"
                    f"price: ${price} ({price_ton}TON)\n"
                    f"change: 5m ({m5}%) "
                    f"1H ({h1}%) "
                    f"6H ({h6}%) "
                    f"24H ({h24}%)\n"
                    f"6H count: {h6_count}\n"
                    f"creation date: {age}\n"
                    f"\n🔹Wallet Balance: {round((wallet_balance * 10**-9),2)} TON (${round((round((wallet_balance * 10**-9),2)*(round(TON_USD_PRICE,2))),2)})"
                    f"\nca: {address}"
                    f"\n🔗 Tx Hash: {trace.transaction.hash}"
                    #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
                    )
                    elif 1000000000 > int(mc) >= 1000000:
                        text = (  
                    f"🌟Buy: {symbol}\n" 
                    f"on {dex}\n" 
                    #f"\n🌟 Transfer: {trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["sum_type"]}"
                    #f"\nType: {trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["sum_type"]}\n"
                    f"\n🔹Wallet: {trace.transaction.account.address.to_userfriendly()}"
                    f"\n🔹Amount: {round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)}" + f" {jetton_name.metadata.symbol}" + f" (${round((round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)*(round(TON_USD_PRICE,2))),2)})"
                    #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
                    #f"\nfor {round((10**-9*float((trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["value"]["min_out"]))),2)} {jetton_to_name.metadata.symbol}\n\n"       
                    f"\n\nmc: ${round((int(mc) * 10**-6), 1)}M\n"
                    f"price: ${price} ({price_ton}TON)\n"
                    f"change: 5m ({m5}%) "
                    f"1H ({h1}%) "
                    f"6H ({h6}%) "
                    f"24H ({h24}%)\n"
                    f"6H count: {h6_count}\n"
                    f"creation date: {age}\n"
                    f"\n🔹Wallet Balance: {round((wallet_balance * 10**-9),2)} TON (${round((round((wallet_balance * 10**-9),2)*(round(TON_USD_PRICE,2))),2)})"
                    f"\nca: {address}"
                    f"\n🔗 Tx Hash: {trace.transaction.hash}"
                    #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
                    )
                    elif 1000000 > int(mc) >= 1000:
                        text = (  
                    f"🌟Buy: {symbol}\n" 
                    f"on {dex}\n" 
                    #f"\n🌟 Transfer: {trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["sum_type"]}"
                    #f"\nType: {trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["sum_type"]}\n"
                    f"\n🔹Wallet: {trace.transaction.account.address.to_userfriendly()}"
                    f"\n🔹Amount: {round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)}" + f" {jetton_name.metadata.symbol}" + f" (${round((round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)*(round(TON_USD_PRICE,2))),2)})"
                    #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
                    #f"\nfor {round((10**-9*float((trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["value"]["min_out"]))),2)} {jetton_to_name.metadata.symbol}\n\n"       
                    f"\n\nmc: ${round((int(mc) * 10**-3),0)}K\n"
                    f"price: ${price} ({price_ton}TON)\n"
                    f"change: 5m ({m5}%) "
                    f"1H ({h1}%) "
                    f"6H ({h6}%) "
                    f"24H ({h24}%)\n"
                    f"6H count: {h6_count}\n"
                    f"creation date: {age}\n"
                    f"\n🔹Wallet Balance: {round((wallet_balance * 10**-9),2)} TON (${round((round((wallet_balance * 10**-9),2)*(round(TON_USD_PRICE,2))),2)})"
                    f"\nca: {address}"
                    f"\n🔗 Tx Hash: {trace.transaction.hash}"
                    #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
                    )
                    
        
        
        url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage" 
        params =  {
        'chat_id': TEXT_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        }
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()  # Raises an error for bad responses
            return response.json()  # Returns the JSON response from Telegram API
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        return None
    



async def main() -> None:
    print("Starting...")
    persistence = PicklePersistence(filepath="wallets")
    application = Application.builder().token(TOKEN).persistence(persistence).build()

    print('Polling...')
    async def subscribe():
        tonapi = AsyncTonapi(api_key=API_KEY)
        while True:
            try:
                print("running...")

                await tonapi.sse.subscribe_to_transactions(
                    accounts=(list(next(zip(*map(str.split, wallet_list))))), handler=handler, args=(tonapi,)
                ) 
            except Exception as e:
                print(f"Error in transaction listener: {e}")
                await asyncio.sleep(1)  # Retry after a delay if there is an error

    await application.initialize()
    await application.start()
    
    # Start the desired mode of communication: webhook or polling
    await application.updater.start_polling()  # For polling mode
    # await application.updater.start_webhook(...)  # Uncomment and configure for webhook mode

    # Start other asyncio tasks, like transaction listeners, in parallel
    listener_task = asyncio.create_task(subscribe())

    try:
        # Keeps the event loop running
        await asyncio.Event().wait()  # Keeps the event loop alive until a signal to stop
    except (KeyboardInterrupt, SystemExit):
        # Handle shutdown signals, such as CTRL+C
        pass
    finally:
        # Clean up and stop all running tasks 
        listener_task.cancel()
        await listener_task

        # Stop the updater and application
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())