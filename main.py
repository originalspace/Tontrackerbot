################################################################
################################################################
######################--FREE BOT--##############################
################################################################
################################################################

from TonTools import *
import typing 
import tonsdk.utils
from pytonapi import *
from pytonapi.schema.events import TransactionEventData
from pytonapi.utils import raw_to_userfriendly
from dexscreener import DexscreenerClient
import logging
import asyncio
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    ConversationHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    CallbackQueryHandler,
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

# Utilities
TOKEN: typing.Final = '<your token>' # Bot Token
BOT_USERNAME: typing.Final = '<your bot name>'
BOT_ID: typing.Final = '<your bot id>' # Bot ID, not used
TEXT_CHAT_ID: typing.Final = "<your chat id>" # Test ID for notifs
API_KEY: typing.Final = '<your token>' # TON CENTER api key
CLIENT = TonCenterClient() 
CLIENT2 = TonApiClient()
TON_USD_PRICE_URL = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"

# TON USD PRICE 
response = requests.get(TON_USD_PRICE_URL)
data = json.loads(response.text)
TON_USD_PRICE = data['rates']['TON']['prices']['USD']

# fetches user chat id from telegem api
while True:
    get_update_url = "https://api.telegram.org/bot7123364221:AAHikC7MG1Fk47S0J7dXMJWFiTYxVQOHo_M/getUpdates"
    response = requests.get(get_update_url)
    data = json.loads(response.text)
    print(data)
    if data["result"] == []: continue
    else: chat_id = data["result"][0]["message"]["chat"]["id"]
    break

 

# Stages
START_ROUTES, RETURN_ADD_ROUTES, RETURN_REMOVE_ROUTES, RETURN_LIST_ROUTES, RETURN_SETTINGS_ROUTES, UPGRADE_ROUTE = range(6)

# Callback data
Add, Remove, Return, List, Settings, Upgrade, Buy_two, Buy_four = range(8)


# List of wallets
wallet_list = [
    #"EQB3ncyBUTjZUA5EnFKR5_EnOMI9V1tTEAAPaiU71gc4TiUt"  This is stonfi wallet#
    ]  


# Start menu  
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [ [ 
        InlineKeyboardButton("🌟Add", callback_data=str(Add)),
        InlineKeyboardButton("🗃️Edit", callback_data=str(Remove)),
    ],[ 
        InlineKeyboardButton("🛠Settings", callback_data=str(Settings)),
        InlineKeyboardButton("💎Upgrade", callback_data=str(Upgrade))
    ],]

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = ("🎯Ton Tracer | Ton Tracker Bot\n\n"
            "This bot allows you to monitor transactions "
            "across the Ton Blockchain. After you have successfully added the wallets " 
            "you wish to monitor, you will be able to recieve immediate notifications " 
            "for any activity.\n\nGet started by adding your first wallet below!"
    )
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return START_ROUTES

# Second menu
async def menu_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()
    keyboard = [ [ 
        InlineKeyboardButton("🌟Add", callback_data=str(Add)),
        InlineKeyboardButton("🗃️Edit", callback_data=str(Remove)),
    ],[ 
        InlineKeyboardButton("🛠Settings", callback_data=str(Settings)),
        InlineKeyboardButton("💎Upgrade", callback_data=str(Upgrade))
    ],]

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = ("🎯 Ton Tracker Bot | Ton Tracer\n\nThis bot allows you to monitor transactions "
            "across the Ton Blockchain. After you have successfully added the wallets " 
            "you wish to monitor, you will recieve immediate notifications" 
            " for any activity."
           
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return START_ROUTES


# Add & Remove buttons
async def add_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("⬅️Return", callback_data=str(Return)),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "✅ - You can now add a wallet.\n\nSimply send a wallet and a name" 
        "\nFor example: WalletAddress Name"
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return RETURN_ADD_ROUTES

async def remove_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wallet = '\n '.join([str(wallets) for wallets in wallet_list])
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("⬅️Return", callback_data=str(Return)),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "✅ - Wallets active - \n"
        "Wallets you are currently following:\n\n"
        f"{wallet}\n\n" 
        "To remove a wallet simply send wallet address"
        "\nFor example: WalletAddress"
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return RETURN_REMOVE_ROUTES


# Add & Remove wallets
async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.text.split(maxsplit=1)

    if len(user) < 2:
        await update.message.reply_text("❗️- Please provide both a wallet address and a name.")
        return
    
    wallet_added, name= user[0], user[1]

    try:
        tonsdk.utils.Address(wallet_added)
        if len(wallet_list) >= 3:
            await update.message.reply_text("❌- You have reached the maximum limit of 3 wallets.")
            return RETURN_REMOVE_ROUTES
        else:
            wallet_list.append(str(wallet_added) + f"  ({name})")
        await update.message.reply_text("🆕 - Wallet added succesfully!")

    except ValueError: 
        await update.message.reply_text("write something valid")


async def remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.text.split(maxsplit=1)

    if len(user) < 1:
        await update.message.reply_text("❗️- Please provide a wallet address.")
        return
    
    wallet_added = user[0]
    tonsdk.utils.Address(wallet_added)
    for wallet_added in wallet_list:
        if wallet_added == wallet_list[0]:
            wallet_list.remove(wallet_added)
            await update.message.reply_text("🚮 - Wallet removed succesfully!")
    

# Sends notifs
async def handler(event: TransactionEventData, tonapi: AsyncTonapi) -> None:
    trace = await tonapi.traces.get_trace(event.tx_hash)

    if trace.transaction.success:
        ########## VARIABLES ##########

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


        # main variables 
        wallet_balance = await Wallet(provider=CLIENT, address=(trace.transaction.account.address.to_userfriendly())).get_balance()
        buy_amount = round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)
        buy_amount_usd = round((round((10**-9*float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2)*(round(TON_USD_PRICE,2))),2)
        token_amount = round((10**-9*float((trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["forward_payload"]["value"]["value"]["min_out"]))),2)
        wallet_balance_usd = round((round((wallet_balance * 10**-9),2)*(round(TON_USD_PRICE,2))),2)

        if jetton_name.metadata.symbol == "pTON":
            if not jetton_to_name.metadata.symbol == "USD₮":
                # jetton buy info
                pairs = await DexscreenerClient().get_token_pairs_async(jetton_to_wallet)
                pair = pairs[0]
                dex = pair.dex_id
                address = pair.base_token.address
                symbol = pair.base_token.symbol
                mc = pair.fdv

                if int(mc) >= 1000000000:
                    text = (    
            f"🟢Buy: {symbol}   mc: ${round((int(mc) * 10**-9), 2)}B\n" 
            f"on {dex}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n☀️Buy: {buy_amount}" + f" TON" + f" (${buy_amount_usd})"
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} {jetton_to_name.metadata.symbol}\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            )
                elif 1000000000 > int(mc) >= 1000000:
                    text = (    
            f"🟢Buy: {symbol}   mc: ${round((int(mc) * 10**-6), 2)}M\n" 
            f"on {dex}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n☀️Buy: {buy_amount}" + f" TON" + f" (${buy_amount_usd})"
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} {jetton_to_name.metadata.symbol}\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            ) 
                elif 1000000 > int(mc) >= 1000:
                    text = (    
            f"🟢Buy: {symbol}   mc: ${round((int(mc) * 10**-3), 2)}K\n" 
            f"on {dex}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n☀️Buy: {buy_amount}" + f" TON" + f" (${buy_amount_usd})"
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} {jetton_to_name.metadata.symbol}\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            )
        elif jetton_to_name.metadata.symbol == "pTON":
            if not jetton_name.metadata.symbol == "USD₮":
                # jetton sell info
                pairs_sell = await DexscreenerClient().get_token_pairs_async(jetton_wallet)
                pair_sell = pairs_sell[0]
                dex_sell = pair_sell.dex_id
                address_sell = pair_sell.base_token.address
                symbol_sell = pair_sell.base_token.symbol
                mc_sell = pair_sell.fdv

                if int(mc_sell) >= 1000000000:
                    text = (    
            f"🛑Sell: {symbol_sell}   mc: ${round((int(mc_sell) * 10**-9), 2)}B\n" 
            f"on {dex_sell}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n💥Sold: {buy_amount}" + f" {jetton_name.metadata.symbol}" 
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} TON"+ f" (${round((token_amount*TON_USD_PRICE),2)})\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address_sell}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            )
                elif 1000000000 > int(mc_sell) >= 1000000:
                    text = (    
            f"🛑Sell: {symbol_sell}   mc: ${round((int(mc_sell) * 10**-6), 2)}M\n" 
            f"on {dex_sell}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n💥Sold: {buy_amount}" + f" {jetton_name.metadata.symbol}" 
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} TON" + f" (${round((token_amount*TON_USD_PRICE),2)})\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address_sell}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            ) 
                elif 1000000 > int(mc_sell) >= 1000:
                    text = (    
            f"🛑Sell: {symbol_sell}   mc: ${round((int(mc_sell) * 10**-3), 2)}K\n" 
            f"on {dex_sell}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n💥Sold: {buy_amount}" + f" {jetton_name.metadata.symbol}" 
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} TON" + f" (${round((token_amount*TON_USD_PRICE),2)})\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address_sell}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            )
        
        if not jetton_name.metadata.symbol == "pTON" and "USD₮":
            if not jetton_to_name.metadata.symbol == "pTON" and "USD₮":
                text =  ( 
            f"♻️Jetton Swap: {symbol}\n" 
            f"on {dex}\n"
            f"\n💎Wallet: {trace.transaction.account.address.to_userfriendly()}"
            f"\n💎Swapped: {buy_amount}" + f" {jetton_name.metadata.symbol}"
            #f" (${round(((round((10**-9 * float(trace.transaction.in_msg.decoded_body["payload"][0]["message"]["message_internal"]["body"]["value"]["value"]["amount"])),2))*(round(TON_USD_PRICE,2))),2)})"
            f"\nfor {token_amount} {jetton_to_name.metadata.symbol}\n"
            f"\n💎Wallet Balance: {round((wallet_balance * 10**-9),2)} TON  (${wallet_balance_usd})"
            f"\nca: {address}"
            f"\n🔗 Tx Hash: {trace.transaction.hash}"
            #"\nTx Link:" + f"{"https://tonviewer.com/transaction/"+trace.transaction.hash}"
            )
        

        url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage" 
        params =  {
        'chat_id': chat_id,
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
    
        

# Settings
async def bot_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("⬅️Return", callback_data=str(Return)),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🔜 - Settings coming soon", reply_markup=reply_markup)
    return RETURN_SETTINGS_ROUTES

# Buy premium 
async def buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [[
        InlineKeyboardButton("BUY 2 TON", callback_data=str(Buy_two)),
        InlineKeyboardButton("BUY 4 TON", callback_data=str(Buy_four)),
    ], [
        InlineKeyboardButton("⬅️Return", callback_data=str(Return)),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "- Your current plan: Free -\n\n"
        "Upgrade your Ton Tracer to track more wallets\n\n"
        "2 Ton: 30 wallets\n"
        "4 Ton: 60 wallets"
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return UPGRADE_ROUTE
async def pay_2_ton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Thank you for your purchase of 30 Wallets!")

async def pay_4_ton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    await update.message.reply_text("Thank you for your purchase of 60 wallets!")

# Running the bot
async def main() -> None:
    print("Starting...")
    persistence = PicklePersistence(filepath="wallets")
    application = Application.builder().token(TOKEN).persistence(persistence).build()
    
    
    conv_handler = ConversationHandler(
        per_message=False,
        entry_points=[CommandHandler("menu", menu_command)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(add_button, pattern="^" + str(Add) + "$"),
                CallbackQueryHandler(remove_button, pattern="^" + str(Remove) + "$"),
                CallbackQueryHandler(bot_setting, pattern="^" + str(Settings) + "$"),
                CallbackQueryHandler(buy_premium, pattern="^" + str(Upgrade) + "$")
            ],
            RETURN_ADD_ROUTES: [
                CallbackQueryHandler(menu_again, pattern="^" + str(Return) + "$"),
                MessageHandler(filters.TEXT &~filters.COMMAND, add_wallet),
            ],
            RETURN_REMOVE_ROUTES: [
                CallbackQueryHandler(menu_again, pattern="^" + str(Return) + "$"),
                MessageHandler(filters.TEXT &~filters.COMMAND, remove_wallet),
            ],
            RETURN_LIST_ROUTES: [
                CallbackQueryHandler(menu_again, pattern="^" + str(Return) + "$"),
                
            ],
            RETURN_SETTINGS_ROUTES: [
                CallbackQueryHandler(menu_again, pattern="^" + str(Return) + "$"),
                
            ],
            UPGRADE_ROUTE: [
                CallbackQueryHandler(pay_2_ton, pattern="^" + str(Buy_two) + "$"),
                CallbackQueryHandler(pay_4_ton, pattern="^" + str(Buy_four) + "$"),
                CallbackQueryHandler(menu_again, pattern="^" + str(Return) + "$")
            ]

        },
        fallbacks=[CommandHandler("menu", menu_command)],
        name = "My_wallets",
        persistent = True, 
    )

    application.add_handler(conv_handler)
    
    
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


    






################################################################
################################################################
######################--PREMIUM BOT--###########################
################################################################
################################################################


