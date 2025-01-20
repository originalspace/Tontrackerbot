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


# EQAukcFwcWR76l0gHiLpvq61_pfo8TiYZyrrvx3_BLuTnhqr

# ['enter', 'best', 'office', 'reopen', 'hurdle', 'combine', 'grit', 'boost', 'mandate', 'game', 'have', 'erupt', 'spare', 'nice', 'treat', 'bread', 'joke', 'naive', 'chronic', 'unveil', 'answer', 'lab', 'soda', 'brief']