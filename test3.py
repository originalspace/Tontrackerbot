from tonutils.client import TonapiClient
from tonutils.wallet import WalletV4R2

# API key for accessing the Tonapi (obtainable from https://tonconsole.com)
API_KEY = "AEMMNEEIGQK4DBAAAAAM4SCIGFCCA22HBRSBW2OVV5VCVZUZQOPE7ME4FYXBT57ZZULGYQY"

# Set to True for test network, False for main network
IS_TESTNET = True

# Mnemonic phrase used to connect the wallet
MNEMONIC: list[str] = []

# The address of the recipient
DESTINATION_ADDRESS = "EQAukcFwcWR76l0gHiLpvq61_pfo8TiYZyrrvx3_BLuTnhqr"

# Optional comment to include in the forward payload
COMMENT = "payment!"

# Amount to transfer in TON
AMOUNT = 2


async def main() -> None:
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, public_key, private_key, mnemonic = WalletV4R2.from_mnemonic(client, MNEMONIC)
    

    tx_hash = await wallet.transfer(
        destination=DESTINATION_ADDRESS,
        amount=AMOUNT,
        body=COMMENT,
    )

    print(f"Successfully transferred {AMOUNT} TON!")
    print(f"Transaction hash: {tx_hash}")
    print(wallet, public_key, private_key, mnemonic)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
