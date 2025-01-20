import asyncio
from TonTools import *


client = TonCenterClient()

new_wallet = Wallet(provider=client)
async def main()-> None:
    print(new_wallet.address)
    print(new_wallet.mnemonics)
    get_balance = await new_wallet.get_balance()
    print(get_balance)

if __name__ == "__main__":
    asyncio.run(main())
