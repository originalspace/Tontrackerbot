from dexscreener import DexscreenerClient, TokenPair
import asyncio

async def main(): 
    client = DexscreenerClient()
    pair = await client.get_token_pair_async("ton", "EQCaY8Ifl2S6lRBMBJeY35LIuMXPc8JfItWG4tl7lBGrSoR2")
    name = pair.base_token.symbol
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
    

    print(
        f"token: {name}\n"
        f"mc: ${mc}\n"
        f"price: ${price} ({price_ton}TON)\n"
        f"Change: 5m ({m5}%) "
        f"1H ({h1}%) "
        f"6H ({h6}%) "
        f"24H ({h24}%)\n"
        f"6H count: {h6_count}\n"
        f"age: {age}"          
          )


if __name__ == "__main__":
    asyncio.run(main())

"""from dexscreener import DexscreenerClient
import asyncio

async def main():
    client = DexscreenerClient()
    

    pairs = await client.get_token_pairs_async("0x2170Ed0880ac9A755fd29B2688956BD959F933F8")

    print(pairs)
    
    
if __name__ == "__main__":
    asyncio.run(main())"""